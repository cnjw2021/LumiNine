'use client';

import { useState, RefObject } from 'react';
import { ResultData } from '@/types/results';

// A4 constants (jsPDF default: 72 DPI)
const A4_WIDTH_PT = 595.28;
const A4_HEIGHT_PT = 841.89;

/**
 * iOS Safari enforces a hard canvas pixel limit (~16.7 megapixels).
 * Beyond this, html2canvas silently produces a blank (0×0) canvas.
 * We use 16 MP as a safe ceiling and automatically reduce `scale`
 * to stay within bounds.
 */
const IOS_CANVAS_MAX_PIXELS = 16_000_000;

/** Detect iOS (iPhone / iPad) regardless of request-desktop mode. */
const isIOS = (): boolean => {
    if (typeof navigator === 'undefined') return false;
    return /iPhone|iPad|iPod/.test(navigator.userAgent) ||
        (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
};

/** Detect Safari (both iOS and macOS), excluding other iOS browsers. */
const isSafari = (): boolean => {
    if (typeof navigator === 'undefined') return false;
    const ua = navigator.userAgent;
    const isSafariLike = /Safari/.test(ua) && !/Chrome/.test(ua) && !/Chromium/.test(ua);
    // Exclude common non-Safari iOS browsers whose UAs also include "Safari".
    const isIOSNonSafari = /CriOS|FxiOS|EdgiOS|OPiOS/.test(ua);
    return isSafariLike && !isIOSNonSafari;
};

/**
 * Calculate a safe html2canvas scale factor.
 *
 * On iOS, if the desired (width × height × scale²) exceeds the 16 MP
 * hard limit, we lower scale automatically so the canvas stays within
 * the memory ceiling. On all other platforms the preferred scale is
 * returned unchanged.
 */
const getSafeScale = (el: HTMLElement, preferredScale: number): number => {
    if (!isIOS()) return preferredScale;

    const w = el.scrollWidth;
    const h = el.scrollHeight;
    const pixels = w * h * preferredScale * preferredScale;

    if (pixels <= IOS_CANVAS_MAX_PIXELS) return preferredScale;

    // Derive the largest scale that fits within the pixel limit.
    const maxScale = Math.sqrt(IOS_CANVAS_MAX_PIXELS / (w * h));

    // If the derived maxScale is invalid, fail fast with a clear error.
    if (!Number.isFinite(maxScale) || maxScale <= 0) {
        const message =
            `[PDF] Failed to compute a valid iOS-safe canvas scale. ` +
            `Element size ${w}×${h} (~${(w * h / 1e6).toFixed(1)} MP) is too large or invalid for the canvas.`;
        console.error(message);
        throw new Error(message);
    }

    const safeScale = Math.min(preferredScale, maxScale);

    console.warn(
        `[PDF] iOS canvas limit hit: ${(pixels / 1e6).toFixed(1)} MP > 16 MP. ` +
        `Reducing scale from ${preferredScale} to ${safeScale.toFixed(2)}.`
    );
    return safeScale;
};

interface UsePdfReportProps {
    resultData: ResultData;
    contentRef: RefObject<HTMLDivElement | null>;
    onActionComplete?: () => void;
}

/**
 * PDF generation hook using html2canvas + jsPDF.
 *
 * The Result component is already laid out at A4 width (794px),
 * so html2canvas captures it at the correct size without any
 * runtime width manipulation.
 *
 * ## Cross-browser defenses (Issue #83)
 * 1. Font loading wait — `document.fonts.ready`
 * 2. iOS Safari canvas memory — auto scale reduction
 * 3. Empty canvas validation — throws on 0×0 capture
 * 4. Safari download fallback — Blob + window.open
 * 5. Fit-to-page scaling — proportional shrink if content exceeds A4 height
 */
export const usePdfReport = ({ resultData, contentRef, onActionComplete }: UsePdfReportProps) => {
    const [isGeneratingPdf, setIsGeneratingPdf] = useState<boolean>(false);

    const handleDownloadPdf = async () => {
        const target = contentRef.current;
        if (!target) {
            console.warn('PDF target element not found. Missing contentRef?');
            return;
        }

        setIsGeneratingPdf(true);

        // Query header outside try so finally can restore its original position
        const header = target.querySelector('.result-header') as HTMLElement | null;
        const originalPosition = header?.style.position ?? '';
        const originalMinHeight = target.style.minHeight;
        // Save original width styles for mobile A4-width force
        const originalWidth = target.style.width;
        const originalMinWidth = target.style.minWidth;
        // Capture original inline display values before hiding (to restore in finally)
        const hiddenEls = target.querySelectorAll('.hide-on-pdf');
        const originalDisplays = Array.from(hiddenEls).map(el => (el as HTMLElement).style.display);

        try {
            // ── 0. Wait for all web fonts to finish loading ──
            // This hook is 'use client' — it only runs in a browser context.
            // Use fonts.ready directly; fallback for legacy browsers without Font Loading API.
            if (document.fonts?.ready) {
                await document.fonts.ready;
            } else {
                await new Promise<void>(resolve => setTimeout(resolve, 50));
            }

            const html2canvas = (await import('html2canvas')).default;
            const { jsPDF } = await import('jspdf');

            // ── 1. Hide non-PDF elements & disable sticky header ──
            hiddenEls.forEach(el => (el as HTMLElement).style.display = 'none');

            if (header) header.style.position = 'static';

            // Temporarily remove minHeight so html2canvas captures only the
            // actual content height and does not add viewport-sized blank space.
            target.style.minHeight = 'unset';

            // ── 1.5. Force A4-width desktop layout for mobile ──
            // On mobile, the viewport is narrower than 794px, causing
            // responsive CSS to stack content into a single column.
            // By forcing 794px and adding a desktop-override class,
            // html2canvas captures the full two-column layout.
            target.style.width = '794px';
            target.style.minWidth = '794px';
            target.classList.add('pdf-capture-mode');

            // ── 2. Determine safe scale (iOS canvas memory defense) ──
            const preferredScale = 2;
            const safeScale = getSafeScale(target, preferredScale);

            // ── 3. Capture the DOM element ──
            const canvas = await html2canvas(target, {
                scale: safeScale,
                useCORS: true,
                backgroundColor: '#f9f7f2',
                logging: false,
            });

            // ── 4. Validate canvas (empty canvas defense) ──
            if (canvas.width === 0 || canvas.height === 0) {
                throw new Error(
                    `html2canvas produced an empty canvas (${canvas.width}×${canvas.height}). ` +
                    'This may indicate a browser memory limit was exceeded.'
                );
            }

            // ── 5. Map image onto A4 — fit-to-page scaling ──
            const imgWidth = A4_WIDTH_PT;
            const imgHeight = (canvas.height * A4_WIDTH_PT) / canvas.width;

            const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' });

            // Always fit to single A4 page.
            // If content exceeds A4 height (e.g. Safari renders taller than Chrome),
            // scale down proportionally so everything fits on one page.
            pdf.setFillColor(249, 247, 242); // #f9f7f2
            pdf.rect(0, 0, A4_WIDTH_PT, A4_HEIGHT_PT, 'F');

            let finalWidth = imgWidth;
            let finalHeight = imgHeight;
            if (imgHeight > A4_HEIGHT_PT) {
                const ratio = A4_HEIGHT_PT / imgHeight;
                finalWidth = imgWidth * ratio;
                finalHeight = A4_HEIGHT_PT;
            }
            // Center horizontally if scaled down (content narrower than A4)
            const xOffset = (A4_WIDTH_PT - finalWidth) / 2;
            pdf.addImage(canvas, 'PNG', xOffset, 0, finalWidth, finalHeight);

            // ── 6. Trigger download (Safari fallback) ──
            // Sanitize user-provided name to remove OS-forbidden filename characters
            const safeName = (resultData.fullName || 'User').replace(/[/\\:*?"<>|]/g, '_').slice(0, 100);
            const fileName = `${safeName}_NineStarKi_Report.pdf`;

            if (isSafari()) {
                // Safari has inconsistent pdf.save() behavior (Blob downloads may be blocked).
                // Always use Blob → window.open() for a reliable experience on Safari.
                const blob = pdf.output('blob');
                const blobUrl = URL.createObjectURL(blob);
                const newWindow = window.open(blobUrl, '_blank', 'noopener,noreferrer');
                if (newWindow) {
                    // Ensure no access to the opener, even if browser ignores features string.
                    newWindow.opener = null;
                } else {
                    // Popup was blocked — fall back to a programmatic download link.
                    const link = document.createElement('a');
                    link.href = blobUrl;
                    link.download = fileName;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
                // Revoke after a short delay so the tab or download can complete
                setTimeout(() => URL.revokeObjectURL(blobUrl), 10_000);
            } else {
                pdf.save(fileName);
            }

            if (onActionComplete) onActionComplete();
        } catch (error) {
            console.error('PDF generation failed:', error);
            alert('PDFの生成に失敗しました。もう一度お試しください。');
        } finally {
            // ── Always restore hidden elements, sticky header & mobile layout ──
            hiddenEls.forEach((el, i) => (el as HTMLElement).style.display = originalDisplays[i] ?? '');
            if (header) header.style.position = originalPosition;
            target.style.minHeight = originalMinHeight;
            target.style.width = originalWidth;
            target.style.minWidth = originalMinWidth;
            target.classList.remove('pdf-capture-mode');
            setIsGeneratingPdf(false);
        }
    };

    return {
        isGeneratingPdf,
        handleDownloadPdf,
    };
};
