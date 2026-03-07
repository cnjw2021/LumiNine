'use client';

import { useState, RefObject } from 'react';
import { ResultData } from '@/types/results';

// A4 constants (jsPDF default: 72 DPI)
const A4_WIDTH_PT = 595.28;
const A4_HEIGHT_PT = 841.89;

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

        try {
            const html2canvas = (await import('html2canvas')).default;
            const { jsPDF } = await import('jspdf');

            // ── 1. Hide non-PDF elements (action buttons) ──
            const hiddenEls = target.querySelectorAll('.hide-on-pdf');
            hiddenEls.forEach(el => (el as HTMLElement).style.display = 'none');

            // ── 2. Capture the DOM element ──
            const canvas = await html2canvas(target, {
                scale: 2,
                useCORS: true,
                backgroundColor: '#f9f7f2',
                logging: false,
            });

            // ── 3. Restore hidden elements ──
            hiddenEls.forEach(el => (el as HTMLElement).style.display = '');

            // ── 4. Map image onto A4 — preserve aspect ratio ──
            const imgWidth = A4_WIDTH_PT;
            const imgHeight = (canvas.height * A4_WIDTH_PT) / canvas.width;

            let finalWidth = imgWidth;
            let finalHeight = imgHeight;

            // If content is taller than A4, scale both dimensions to fit
            if (imgHeight > A4_HEIGHT_PT) {
                const ratio = A4_HEIGHT_PT / imgHeight;
                finalWidth = imgWidth * ratio;
                finalHeight = A4_HEIGHT_PT;
            }

            // Centre horizontally if scaled down
            const xOffset = (A4_WIDTH_PT - finalWidth) / 2;

            // ── 5. Build PDF and trigger download ──
            const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' });

            // Fill entire page with content background color (hides any margins)
            pdf.setFillColor(249, 247, 242); // #f9f7f2
            pdf.rect(0, 0, A4_WIDTH_PT, A4_HEIGHT_PT, 'F');

            const imgData = canvas.toDataURL('image/png');
            pdf.addImage(imgData, 'PNG', xOffset, 0, finalWidth, finalHeight);

            const fileName = `${resultData.fullName || 'User'}_NineStarKi_Report.pdf`;
            pdf.save(fileName);

            if (onActionComplete) onActionComplete();
        } catch (error) {
            console.error('PDF generation failed:', error);
            alert('PDFの生成に失敗しました。もう一度お試しください。');
        } finally {
            setIsGeneratingPdf(false);
        }
    };

    return {
        isGeneratingPdf,
        pdfProgress: isGeneratingPdf ? 50 : 0,
        handleDownloadPdf,
    };
};
