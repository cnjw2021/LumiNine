#!/usr/bin/env node
/**
 * pr-review-reply.js — GitHub PR 리뷰 코멘트 일괄 reply 자동화
 *
 * 사용법:
 *   node scripts/pr-review-reply.js [옵션]
 *
 * 옵션:
 *   --batch-file <path>          처리할 배치 JSON 파일 경로 (필수)
 *   --continue-on-error          오류 발생 시 중단하지 않고 계속
 *   --failed-batch-out <path>    실패한 항목을 저장할 JSON 경로
 *   --log-file <path>            처리 결과 ndjson 로그 파일
 *   --handled-urls <path>        처리 완료 URL 누적 목록 JSON (자동 업데이트)
 *
 * 배치 JSON 형식 (pr-triage.js 출력과 동일):
 * [
 *   {
 *     "thread_id": "PRRT_...",
 *     "comment_id": 123456,
 *     "comment_url": "https://github.com/.../pull/9#discussion_r...",
 *     "path": "...",
 *     "action": "reply_and_resolve" | "reply",
 *     "reply_body": "reply 문자열"
 *   },
 *   ...
 * ]
 *
 * 필요 환경:
 *   - `gh` CLI 설치/인증 완료
 *   - Node.js 18+
 */

const { execSync, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ── CLI 파싱 ──────────────────────────────────────────────
const args = process.argv.slice(2);
const getFlag = (flag, defaultVal = null, requireValue = false) => {
    const idx = args.indexOf(flag);
    if (idx === -1) return defaultVal;
    const next = args[idx + 1];
    if (next === undefined || next.startsWith('--')) {
        if (requireValue) {
            console.error(`❌ ${flag} 옵션에는 값이 필요합니다.`);
            console.error('사용법: node scripts/pr-review-reply.js --batch-file <path> [옵션]');
            process.exit(1);
        }
        return defaultVal;
    }
    return next;
};

const batchFilePath = getFlag('--batch-file', null, true);
const continueOnError = args.includes('--continue-on-error');
const failedBatchOut = getFlag('--failed-batch-out', null, true);
const logFilePath = getFlag('--log-file', null, true);
const handledUrlsPath = getFlag('--handled-urls', null, true);

if (!batchFilePath) {
    console.error('❌ --batch-file 옵션이 필요합니다.');
    process.exit(1);
}


if (!fs.existsSync(batchFilePath)) {
    console.error(`❌ 배치 파일을 찾을 수 없습니다: ${batchFilePath}`);
    process.exit(1);
}

// ── 배치 로드 ─────────────────────────────────────────────
const batch = JSON.parse(fs.readFileSync(batchFilePath, 'utf-8'));
if (!Array.isArray(batch) || batch.length === 0) {
    console.log('⚠️  배치가 비어 있거나 형식이 잘못되었습니다. 종료합니다.');
    process.exit(0);
}

// ── handled URLs 로드 ─────────────────────────────────────
let handledUrls = new Set();
if (handledUrlsPath && fs.existsSync(handledUrlsPath)) {
    try {
        const raw = JSON.parse(fs.readFileSync(handledUrlsPath, 'utf-8'));
        handledUrls = new Set(Array.isArray(raw) ? raw : Object.keys(raw));
    } catch { /* ignore */ }
}

// ── 저장소 정보 추출 (첫 번째 항목 URL 기준) ─────────────
function parseRepoFromUrl(url) {
    // https://github.com/OWNER/REPO/pull/N#discussion_rXXX
    const m = url.match(/github\.com\/([^/]+)\/([^/]+)\/pull\/(\d+)/);
    return m ? { owner: m[1], repo: m[2], pr: parseInt(m[3], 10) } : null;
}

const repoInfo = parseRepoFromUrl(batch[0].comment_url);
if (!repoInfo) {
    console.error('❌ comment_url에서 저장소 정보를 파싱할 수 없습니다.');
    process.exit(1);
}
const { owner, repo, pr: PR } = repoInfo;

// ── 현재 git 커밋 해시 취득 ──────────────────────────────
let commitHash = '';
try {
    commitHash = execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim();
    console.log(`📌 대응 커밋 해시: ${commitHash}`);
} catch {
    console.warn('⚠️  git commit hash 취득 실패. reply에 해시 미포함.');
}


console.log(`\n🚀 PR #${PR} 리뷰 reply 배치 처리 시작 (${batch.length}건)\n`);

const succeeded = [];
const failed = [];
const logEntries = [];

function ghExec(cmd) {
    return execSync(cmd, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
}

function ghGraphqlMutation(query, variables) {
    const args = ['api', 'graphql', '-f', `query=${query}`];
    for (const [key, value] of Object.entries(variables)) {
        args.push('-f', `${key}=${value}`);
    }
    return execFileSync('gh', args, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
}

for (const item of batch) {
    const { thread_id, comment_id, comment_url, path: filePath, action, reply_body } = item;

    // 이미 처리한 URL 스킵
    if (handledUrls.has(comment_url)) {
        console.log(`⏭️  스킵(already handled): ${comment_url}`);
        continue;
    }

    console.log(`\n→ 처리 중: ${filePath || comment_url}`);
    console.log(`  action: ${action}, thread: ${thread_id}`);

    const logEntry = {
        timestamp: new Date().toISOString(),
        thread_id,
        comment_id,
        comment_url,
        action,
        status: null,
        error: null,
    };

    try {
        // 1) reply 작성
        if (reply_body) {
            // 커밋 해시 footer 자동 추가
            const hashFooter = commitHash
                ? `\n\n> 📌 대응 커밋: \`${commitHash}\``
                : '';
            const finalReplyBody = reply_body + hashFooter;

            const replyMutation = `
mutation($id: ID!, $body: String!) {
  addPullRequestReviewThreadReply(input: {
    pullRequestReviewThreadId: $id
    body: $body
  }) {
    comment { id url }
  }
}`;
            ghGraphqlMutation(replyMutation, { id: thread_id, body: finalReplyBody });
            console.log(`  ✅ reply 등록 완료`);
        }


        // 2) resolve (action === 'reply_and_resolve')
        if (action === 'reply_and_resolve') {
            const resolveMutation = `
mutation($id: ID!) {
  resolveReviewThread(input: { threadId: $id }) {
    thread { id isResolved }
  }
}`;
            ghGraphqlMutation(resolveMutation, { id: thread_id });
            console.log(`  ✅ thread resolve 완료`);
        }

        logEntry.status = 'success';
        succeeded.push(item);
        handledUrls.add(comment_url);

    } catch (err) {
        const errMsg = err.stderr || err.message || String(err);
        console.error(`  ❌ 실패: ${errMsg.slice(0, 200)}`);
        logEntry.status = 'failed';
        logEntry.error = errMsg.slice(0, 500);
        failed.push(item);
    } finally {
        // 성공/실패 모두 로그에 기록 (break 전 마지막 항목도 포함)
        logEntries.push(logEntry);
    }

    if (logEntry.status === 'failed' && !continueOnError) {
        console.error('\n중단합니다 (--continue-on-error 없음)');
        break;
    }
}

// ── 로그 기록 ─────────────────────────────────────────────
if (logFilePath && logEntries.length > 0) {
    fs.mkdirSync(path.dirname(logFilePath), { recursive: true });
    const ndjson = logEntries.map(e => JSON.stringify(e)).join('\n') + '\n';
    fs.appendFileSync(logFilePath, ndjson, 'utf-8');
    console.log(`\n📝 로그 저장: ${logFilePath}`);
}

// ── 실패 배치 저장 ────────────────────────────────────────
if (failedBatchOut && failed.length > 0) {
    fs.mkdirSync(path.dirname(failedBatchOut), { recursive: true });
    fs.writeFileSync(failedBatchOut, JSON.stringify(failed, null, 2), 'utf-8');
    console.log(`⚠️  실패 배치 저장: ${failedBatchOut} (${failed.length}건)`);
}

// ── handled URLs 업데이트 ─────────────────────────────────
if (handledUrlsPath) {
    fs.mkdirSync(path.dirname(handledUrlsPath), { recursive: true });
    // Set을 배열로 변환하여 저장
    fs.writeFileSync(handledUrlsPath, JSON.stringify([...handledUrls], null, 2), 'utf-8');
}

// ── 완료 요약 ─────────────────────────────────────────────
console.log(`
=== Reply 배치 처리 완료 ===
  성공: ${succeeded.length}건
  실패: ${failed.length}건
  스킵: ${batch.length - succeeded.length - failed.length}건
`);

if (failed.length > 0) process.exit(1);
