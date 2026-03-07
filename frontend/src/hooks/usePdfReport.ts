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

/** Detect Safari (both iOS and macOS). */
const isSafari = (): boolean => {
    if (typeof navigator === 'undefined') return false;
    const ua = navigator.userAgent;
    return /Safari/.test(ua) && !/Chrome/.test(ua) && !/Chromium/.test(ua);
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

    // Derive the largest integer-friendly scale that fits.
    const maxScale = Math.sqrt(IOS_CANVAS_MAX_PIXELS / (w * h));
    const safeScale = Math.max(1, Math.floor(maxScale));

    console.warn(
        `[PDF] iOS canvas limit hit: ${(pixels / 1e6).toFixed(1)} MP > 16 MP. ` +
        `Reducing scale from ${preferredScale} to ${safeScale}.`
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
 * 5. Multi-page auto-split — A4-height slicing
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

        try {
            // ── 0. Wait for all web fonts to finish loading ──
            await document.fonts.ready;

            const html2canvas = (await import('html2canvas')).default;
            const { jsPDF } = await import('jspdf');

            // ── 1. Hide non-PDF elements & disable sticky header ──
            const hiddenEls = target.querySelectorAll('.hide-on-pdf');
            hiddenEls.forEach(el => (el as HTMLElement).style.display = 'none');

            if (header) header.style.position = 'static';

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

            // ── 5. Map image onto A4 — multi-page auto-split ──
            const imgWidth = A4_WIDTH_PT;
            const imgHeight = (canvas.height * A4_WIDTH_PT) / canvas.width;

            const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' });
            const imgData = canvas.toDataURL('image/png');

            if (imgHeight <= A4_HEIGHT_PT) {
                // Single page — centre content
                const xOffset = (A4_WIDTH_PT - imgWidth) / 2;
                pdf.setFillColor(249, 247, 242); // #f9f7f2
                pdf.rect(0, 0, A4_WIDTH_PT, A4_HEIGHT_PT, 'F');
                pdf.addImage(imgData, 'PNG', xOffset, 0, imgWidth, imgHeight);
            } else {
                // Multi-page — slice by A4 height
                const totalPages = Math.ceil(imgHeight / A4_HEIGHT_PT);
                for (let page = 0; page < totalPages; page++) {
                    if (page > 0) pdf.addPage();
                    pdf.setFillColor(249, 247, 242);
                    pdf.rect(0, 0, A4_WIDTH_PT, A4_HEIGHT_PT, 'F');
                    pdf.addImage(
                        imgData, 'PNG',
                        0, -(page * A4_HEIGHT_PT),
                        imgWidth, imgHeight
                    );
                }
            }

            // ── 6. Trigger download (Safari fallback) ──
            const fileName = `${resultData.fullName || 'User'}_NineStarKi_Report.pdf`;

            if (isSafari()) {
                // Safari may block pdf.save() blob downloads.
                // Open the PDF in a new tab instead, which Safari handles reliably.
                const blob = pdf.output('blob');
                const blobUrl = URL.createObjectURL(blob);
                window.open(blobUrl, '_blank');
                // Revoke after a short delay so the tab can load
                setTimeout(() => URL.revokeObjectURL(blobUrl), 10_000);
            } else {
                pdf.save(fileName);
            }

            if (onActionComplete) onActionComplete();
        } catch (error) {
            console.error('PDF generation failed:', error);
            alert('PDFの生成に失敗しました。もう一度お試しください。');
        } finally {
            // ── Always restore hidden elements & sticky header ──
            const hiddenEls = target.querySelectorAll('.hide-on-pdf');
            hiddenEls.forEach(el => (el as HTMLElement).style.display = '');
            if (header) header.style.position = originalPosition;
            setIsGeneratingPdf(false);
        }
    };

    return {
        isGeneratingPdf,
        handleDownloadPdf,
    };
};
