#!/usr/bin/env node
/**
 * pr-triage.js — GitHub PR 리뷰 코멘트 triage 자동화
 *
 * 사용법:
 *   node scripts/pr-triage.js <PR 번호> [옵션]
 *
 * 옵션:
 *   --limit-auto-fix <N>          auto-fixable 배치 상한 (기본 5)
 *   --offset-auto-fix <N>         auto-fixable 배치 시작 오프셋 (기본 0)
 *   --emit-reply-batch            pr-<PR>-reply-batch.json 생성 (auto-fix 용)
 *   --emit-manual-reply-batch     pr-<PR>-manual-reply-batch.json 생성 (manual/design 용)
 *   --repo <OWNER/REPO>           대상 GitHub 저장소 (기본: GITHUB_REPOSITORY 또는 현재 gh 설정)
 *   --pr-review-dir <path>        출력 디렉터리 (기본: .pr-review)
 *   --include-resolved            resolved 코멘트도 포함 (정정 reply 용)
 *   --handled-urls <path>         이미 처리된 코멘트 URL 목록 JSON
 *
 * 출력 파일 (PR_REVIEW_DIR = .pr-review/):
 *   .pr-review/pr-<PR>-triage.md              — triage 결과 마크다운
 *   .pr-review/pr-<PR>-autofix-checklist.md   — auto-fixable 체크리스트
 *   .pr-review/pr-<PR>-reply-batch.json       — gh API 일괄 reply 배치
 *   .pr-review/pr-<PR>-manual-reply-batch.json — manual reply 배치
 *
 * 필요 환경:
 *   - `gh` CLI 설치/인증 완료
 *   - Node.js 18+
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ── CLI 인수 파싱 ──────────────────────────────────────────
const args = process.argv.slice(2);
const PR = parseInt(args[0], 10);
if (!PR || isNaN(PR)) {
    console.error('사용법: node scripts/pr-triage.js <PR 번호> [옵션]');
    process.exit(1);
}

/**
 * 값이 필요한 플래그 (--foo bar) 를 파싱한다.
 * 값이 없거나 다음 토큰이 '--'로 시작하면 defaultVal 을 반환한다.
 * requireValue=true 일 때 값이 없으면 오류 메시지를 출력하고 프로세스를 종료한다.
 */
const getFlag = (flag, defaultVal = null, requireValue = false) => {
    const idx = args.indexOf(flag);
    if (idx === -1) return defaultVal;
    const next = args[idx + 1];
    if (next === undefined || next.startsWith('--')) {
        if (requireValue) {
            console.error(`❌ ${flag} 옵션에 값이 필요합니다.`);
            console.error('사용법: node scripts/pr-triage.js <PR 번호> [옵션]');
            process.exit(1);
        }
        return defaultVal;
    }
    return next;
};

const limitAutoFix = parseInt(getFlag('--limit-auto-fix', '5'), 10);
const offsetAutoFix = parseInt(getFlag('--offset-auto-fix', '0'), 10);
const emitReplyBatch = args.includes('--emit-reply-batch');
const emitManualReplyBatch = args.includes('--emit-manual-reply-batch');
const includeResolved = args.includes('--include-resolved');
const handledUrlsPath = getFlag('--handled-urls', null);

const prReviewDirFromFlag = getFlag('--pr-review-dir', null);
const PR_REVIEW_DIR = prReviewDirFromFlag || process.env.PR_REVIEW_DIR || '.pr-review';
fs.mkdirSync(PR_REVIEW_DIR, { recursive: true });


// ── handled URLs 로드 ─────────────────────────────────────
let handledUrls = new Set();
if (handledUrlsPath && fs.existsSync(handledUrlsPath)) {
    try {
        const raw = JSON.parse(fs.readFileSync(handledUrlsPath, 'utf-8'));
        handledUrls = new Set(Array.isArray(raw) ? raw : Object.keys(raw));
    } catch { /* ignore */ }
}

// ── 저장소 owner/name 결정 ────────────────────────────────
// 우선순위: 1) --repo OWNER/REPO CLI 옵션
//           2) GITHUB_REPOSITORY 환경변수 (GitHub Actions)
//           3) gh repo view --json owner,name 자동 조회
const repoArg = getFlag('--repo', null);
let repoOwner = null;
let repoName = null;

if (repoArg) {
    const parts = repoArg.split('/');
    if (parts.length === 2 && parts[0] && parts[1]) {
        repoOwner = parts[0]; repoName = parts[1];
    } else {
        console.error('❌ --repo 옵션은 "OWNER/REPO" 형식이어야 합니다.');
        process.exit(1);
    }
} else if (process.env.GITHUB_REPOSITORY) {
    const parts = process.env.GITHUB_REPOSITORY.split('/');
    if (parts.length === 2) { repoOwner = parts[0]; repoName = parts[1]; }
}

if (!repoOwner || !repoName) {
    try {
        const out = execSync('gh repo view --json owner,name', { encoding: 'utf8' });
        const info = JSON.parse(out);
        repoOwner = (info.owner && (info.owner.login || info.owner)) || repoOwner;
        repoName = info.name || repoName;
    } catch (e) {
        console.error('❌ 현재 리포지토리를 자동으로 조회하지 못했습니다.');
        console.error('   --repo OWNER/REPO 옵션 또는 GITHUB_REPOSITORY 환경변수를 설정해 주세요.');
        process.exit(1);
    }
}

let prData = null;
let allThreads = [];
let hasNextPage = true;
let cursor = null;

try {
    while (hasNextPage) {
        const query = `
        {
          repository(owner: "${repoOwner}", name: "${repoName}") {
            pullRequest(number: ${PR}) {
              title
              reviewThreads(first: 50${cursor ? `, after: "${cursor}"` : ''}) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  id
                  isResolved
                  isOutdated
                  path
                  line
                  startLine
                  diffSide
                  comments(first: 10) {
                    totalCount
                    nodes {
                      id
                      databaseId
                      author { login }
                      body
                      url
                      createdAt
                    }
                  }
                }
              }
            }
          }
        }
        `;
        const result = execSync(`gh api graphql -f query='${query.replace(/'/g, "'\\''")}'`, {
            encoding: 'utf-8',
            stdio: ['pipe', 'pipe', 'pipe'],
            maxBuffer: 10 * 1024 * 1024 // 10MB
        });
        const data = JSON.parse(result).data.repository.pullRequest;
        if (!prData) prData = data;

        allThreads.push(...data.reviewThreads.nodes);
        hasNextPage = data.reviewThreads.pageInfo.hasNextPage;
        cursor = data.reviewThreads.pageInfo.endCursor;
    }
} catch (e) {
    console.error('❌ GitHub API 조회 실패:', e.message);
    process.exit(1);
}

// 코멘트 누락 경고 (지적 사항 [M1] 대응)
allThreads.forEach(t => {
    if (t.comments.totalCount > 10) {
        console.warn(`⚠️ Warning: Thread ${t.id} has ${t.comments.totalCount} comments, but only 10 were fetched.`);
    }
});
const copilotThreads = allThreads.filter(t =>
    t.comments.nodes.length > 0 &&
    t.comments.nodes[0].author.login === 'copilot-pull-request-reviewer' &&
    (includeResolved || !t.isResolved)
);

console.log(`✅ 전체 스레드: ${allThreads.length}, Copilot 지적: ${copilotThreads.length}`);

// ── triage 분류 ───────────────────────────────────────────
// 우선순위: suggestion 코드블록 → auto-fixable 키워드 → design 키워드 → manual
const AUTO_FIX_KEYWORDS = [
    '제거', '삭제', '수정', 'import', '추가', 'suggestion', '변경',
    'replace', 'remove', 'fix', 'add', 'update', 'rename',
    'timedelta', 'refactor', '리팩',
];
const DESIGN_KEYWORDS = [
    // suggestion 포함 코드블록이 없는 경우에만 적용
    '설계', 'design review', 'architecture', '아키텍처',
    '구조를 정리', '정리해 주세요', '방식을 고려', '캡슐화',
    '일관성', '의존성 방향', 'clean architecture', '결합도',
];

function classify(thread) {
    const body = thread.comments.nodes[0].body;
    console.log(`  Checking thread at ${thread.path}:${thread.line} - Body snippet: ${body.slice(0, 50).replace(/\n/g, ' ')}...`);
    const bodyLower = body.toLowerCase();
    const url = thread.comments.nodes[0].url;
    if (handledUrls.has(url)) return { category: 'handled', reason: 'handled_url' };
    // suggestion 코드블록이 있으면 무조건 auto-fixable
    if (body.includes('```suggestion')) return { category: 'auto-fixable', reason: 'suggestion_codeblock' };
    // auto-fix 키워드가 design 키워드보다 우선
    if (AUTO_FIX_KEYWORDS.some(k => bodyLower.includes(k.toLowerCase()))) return { category: 'auto-fixable', reason: 'autofix_keyword' };
    // design 키워드
    if (DESIGN_KEYWORDS.some(k => bodyLower.includes(k.toLowerCase()))) return { category: 'design', reason: 'design_keyword' };
    return { category: 'manual', reason: 'default_manual' };
}

const classified = copilotThreads.map(t => {
    const cat = classify(t);
    console.log(`    Categorized as: ${cat.category} (${cat.reason})`);
    return { ...t, _category: cat.category, _reason: cat.reason };
});
const autoFixable = classified.filter(t => t._category === 'auto-fixable');
const manual = classified.filter(t => t._category === 'manual');
const design = classified.filter(t => t._category === 'design');
const handled = classified.filter(t => t._category === 'handled');

// ── 배치 슬라이스 ─────────────────────────────────────────
const batchAutoFix = autoFixable.slice(offsetAutoFix, offsetAutoFix + limitAutoFix);

// ── triage.md 출력 ────────────────────────────────────────
const triagePath = path.join(PR_REVIEW_DIR, `pr-${PR}-triage.md`);
const now = new Date().toISOString();

let md = `# PR #${PR} Copilot 리뷰 Triage — ${now}

**제목:** ${prData.title}

## 요약
- Total: ${copilotThreads.length}
- Auto-fixable: ${autoFixable.length} (이번 배치: ${batchAutoFix.length}/${autoFixable.length})
- Needs Manual Verification: ${manual.length}
- Needs design review: ${design.length}
- Already handled: ${handled.length}

${offsetAutoFix > 0 ? `- Auto-fixable included in this batch: ${batchAutoFix.length}/${autoFixable.length}` : ''}

---

## 🔧 Auto-fixable (배치 ${offsetAutoFix + 1}~${offsetAutoFix + batchAutoFix.length} / 전체 ${autoFixable.length})\n\n`;

batchAutoFix.forEach((t, i) => {
    const c = t.comments.nodes[0];
    md += `### [${offsetAutoFix + i + 1}] ${t.path}${t.line ? `:${t.line}` : ''}\n`;
    md += `- **URL:** ${c.url}\n`;
    md += `- **Thread ID:** ${t.id}\n`;
    md += `- **Comment ID:** ${c.databaseId}\n`;
    md += `\n${c.body}\n\n---\n\n`;
});

if (manual.length > 0) {
    md += `## 🔍 Manual Verification 필요\n\n`;
    manual.forEach((t, i) => {
        const c = t.comments.nodes[0];
        md += `### [M${i + 1}] ${t.path}${t.line ? `:${t.line}` : ''}\n`;
        md += `- **URL:** ${c.url}\n\n${c.body}\n\n---\n\n`;
    });
}

if (design.length > 0) {
    md += `## 🏗️ Design Review 필요\n\n`;
    design.forEach((t, i) => {
        const c = t.comments.nodes[0];
        md += `### [D${i + 1}] ${t.path}${t.line ? `:${t.line}` : ''}\n`;
        md += `- **URL:** ${c.url}\n\n${c.body}\n\n---\n\n`;
    });
}

fs.writeFileSync(triagePath, md, 'utf-8');
console.log(`\n📄 triage.md 생성: ${triagePath}`);

// ── autofix-checklist.md ──────────────────────────────────
const checklistPath = path.join(PR_REVIEW_DIR, `pr-${PR}-autofix-checklist.md`);
let checklist = `# PR #${PR} Auto-fix 체크리스트\n\n`;
batchAutoFix.forEach((t, i) => {
    const c = t.comments.nodes[0];
    checklist += `- [ ] [${offsetAutoFix + i + 1}] ${t.path}${t.line ? `:${t.line}` : ''} — ${c.url}\n`;
});
fs.writeFileSync(checklistPath, checklist, 'utf-8');
console.log(`📋 autofix-checklist.md 생성: ${checklistPath}`);

// ── reply-batch.json (auto-fixable) ──────────────────────
if (emitReplyBatch) {
    const batch = batchAutoFix.map(t => {
        const c = t.comments.nodes[0];
        return {
            thread_id: t.id,
            comment_id: c.databaseId,
            comment_url: c.url,
            path: t.path,
            line: t.line,
            body: c.body.substring(0, 80).replace(/\n/g, ' '),
            action: 'reply_and_resolve',
            reply_body: '✅ 지적 사항 반영 완료했습니다. 코드를 수정/확인해 주세요.',
        };
    });
    const batchPath = path.join(PR_REVIEW_DIR, `pr-${PR}-reply-batch.json`);
    fs.writeFileSync(batchPath, JSON.stringify(batch, null, 2), 'utf-8');
    console.log(`📦 reply-batch.json 생성: ${batchPath} (${batch.length}건)`);
}

// ── manual-reply-batch.json ───────────────────────────────
if (emitManualReplyBatch) {
    const manualBatch = [...manual, ...design].map(t => {
        const c = t.comments.nodes[0];
        return {
            thread_id: t.id,
            comment_id: c.databaseId,
            comment_url: c.url,
            path: t.path,
            line: t.line,
            body: c.body.substring(0, 80).replace(/\n/g, ' '),
            action: 'reply',
            reply_body: '✅ 검토했습니다. 해당 설계/수동 검증 사항을 반영했습니다.',
        };
    });
    const manualBatchPath = path.join(PR_REVIEW_DIR, `pr-${PR}-manual-reply-batch.json`);
    fs.writeFileSync(manualBatchPath, JSON.stringify(manualBatch, null, 2), 'utf-8');
    console.log(`📦 manual-reply-batch.json 생성: ${manualBatchPath} (${manualBatch.length}건)`);
}

// ── 완료 요약 ─────────────────────────────────────────────
console.log(`
=== Triage 완료 ===
  Auto-fixable : ${autoFixable.length} (이번 배치: ${batchAutoFix.length})
  Manual       : ${manual.length}
  Design       : ${design.length}
  Handled      : ${handled.length}
`);
