'use client';

import React, { useState, useEffect } from 'react';
import { Flex, Transition } from '@mantine/core';
import { IconChevronDown } from '@tabler/icons-react';
import { COLORS } from '@/utils/theme';

/**
 * スクロールインジケーター
 *
 * SRP: スクロール可否の検出と視覚的ヒントの表示のみを担当
 */

/** スクロールコンテナのCSSセレクター */
const SCROLL_CONTAINER_SELECTOR = '.mantine-Drawer-body';

/** グラデーション背景 */
const GRADIENT_BG = 'linear-gradient(to top, rgba(249, 247, 242, 0.95) 0%, rgba(249, 247, 242, 0) 100%)';

interface ScrollIndicatorProps {
    /** スクロール可否の再計算トリガー (個別プリミティブ値) */
    isLoggedIn: boolean;
    permissionsLoaded: boolean;
    adminMenuCount: number;
}

export const ScrollIndicator = ({ isLoggedIn, permissionsLoaded, adminMenuCount }: ScrollIndicatorProps) => {
    const [showScrollIndicator, setShowScrollIndicator] = useState(false);

    useEffect(() => {
        const checkScroll = () => {
            const container = document.querySelector(SCROLL_CONTAINER_SELECTOR);
            if (container) {
                const hasOverflow = container.scrollHeight > container.clientHeight;
                setShowScrollIndicator(hasOverflow);
            }
        };

        checkScroll();
        window.addEventListener('resize', checkScroll);
        return () => window.removeEventListener('resize', checkScroll);
    }, [isLoggedIn, permissionsLoaded, adminMenuCount]);

    return (
        <Transition mounted={showScrollIndicator} transition="fade" duration={200}>
            {(styles) => (
                <Flex
                    justify="center"
                    align="center"
                    style={{
                        ...styles,
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        padding: '10px',
                        background: GRADIENT_BG,
                        pointerEvents: 'none',
                    }}
                >
                    <IconChevronDown size={20} color={COLORS.accent} style={{ opacity: 0.7 }} />
                </Flex>
            )}
        </Transition>
    );
};
