'use client';

import { useState, useEffect } from 'react';
import api from '@/utils/api';
import { ResultData, PdfJobResultDataMinimal } from '@/types/results';

interface UsePdfReportProps {
    resultData: ResultData;
    onActionComplete?: () => void;
}

export const usePdfReport = ({ resultData, onActionComplete }: UsePdfReportProps) => {
    const [isGeneratingPdf, setIsGeneratingPdf] = useState<boolean>(false);
    const [pdfProgress, setPdfProgress] = useState<number>(0);
    const [browserType, setBrowserType] = useState<'safari' | 'chrome' | 'other'>('other');

    // ブラウザを検出する関数
    const detectBrowser = (): 'safari' | 'chrome' | 'other' => {
        if (typeof window === 'undefined') return 'other';
        const userAgent = window.navigator.userAgent.toLowerCase();
        if (userAgent.indexOf('safari') !== -1 && userAgent.indexOf('chrome') === -1) {
            return 'safari';
        } else if (userAgent.indexOf('chrome') !== -1) {
            return 'chrome';
        }
        return 'other';
    };

    // ブラウザ検出
    useEffect(() => {
        setBrowserType(detectBrowser());
    }, []);

    // 共通のPDFダウンロード関数
    const downloadPdf = async (templateId: number, useSimple: boolean) => {
        try {
            setIsGeneratingPdf(true);
            setPdfProgress(0);

            const normalizedBirthdate = (resultData.birthdate || '').replace(/\//g, '-');
            const minimalResultData: PdfJobResultDataMinimal = {
                fullName: resultData.fullName,
                birthdate: normalizedBirthdate,
                gender: (resultData as any).gender, // ResultData type might need gender adjustment or casting
                targetYear: resultData.targetYear || new Date().getFullYear(),
            };

            // 1. ジョブ登録
            const createRes = await api.post('/pdf-jobs', {
                resultData: minimalResultData,
                templateId,
                backgroundId: templateId,
                useSimple,
            });

            const jobId: string = createRes.data.job_id;
            setPdfProgress(0);

            // 2. ポーリングでステータス確認
            const pollInterval = 3000;
            const wait = (ms: number) => new Promise((res) => setTimeout(res, ms));

            while (true) {
                const statusRes = await api.get(`/pdf-jobs/${jobId}`);
                const { status, download_url } = statusRes.data;

                if (status === 'queued') {
                    setPdfProgress(10);
                } else if (status === 'started') {
                    setPdfProgress((prev) => (prev < 90 ? prev + 10 : prev));
                }

                if (status === 'finished') {
                    setPdfProgress(100);
                    window.location.href = download_url;
                    await wait(600);
                    break;
                }

                if (status === 'failed') {
                    throw new Error('PDF生成に失敗しました。');
                }

                await wait(pollInterval);
            }

            if (onActionComplete) onActionComplete();
        } catch (error) {
            console.error('PDFの非同期生成中にエラーが発生しました:', error);
            alert('PDFの生成に失敗しました。もう一度お試しください。');
        } finally {
            setPdfProgress(0);
            setIsGeneratingPdf(false);
        }
    };

    const handleDownloadPdf = async (templateId: number) => {
        await downloadPdf(templateId, false);
    };

    const handlePreviewReport = async (templateId: number) => {
        const useSimple = browserType === 'safari';

        try {
            setIsGeneratingPdf(true);

            const response = await api.post('/nine-star/preview-report',
                {
                    resultData,
                    templateId,
                    backgroundId: templateId,
                    useSimple,
                },
                { responseType: 'text' }
            );

            const newWindow = window.open('', '_blank');
            if (newWindow) {
                newWindow.document.write(response.data);
                newWindow.document.close();
            } else {
                alert('プレビューを表示できません。ポップアップがブロックされている可能性があります。');
            }

            if (onActionComplete) onActionComplete();
        } catch (error) {
            console.error('プレビュー表示中にエラーが発生しました:', error);
            alert('プレビューの表示に失敗しました。もう一度お試しください。');
        } finally {
            setIsGeneratingPdf(false);
        }
    };

    return {
        isGeneratingPdf,
        pdfProgress,
        handleDownloadPdf,
        handlePreviewReport,
    };
};
