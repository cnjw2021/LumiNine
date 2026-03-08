"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Container, Loader } from '@mantine/core';
import { ReadingForm } from '@/components/features/form';
import { useAuth } from '@/contexts/auth/AuthContext';

export default function AppraisalPage() {
    const { token, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !token) {
            router.replace('/login');
        }
    }, [isLoading, token, router]);


    if (isLoading) {
        return (
            <Container style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <Loader />
            </Container>
        );
    }

    if (!token) {
        return null;
    }

    return (
        <Container
            size="lg"
            py="xl"
            style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'flex-start',
                paddingTop: 'calc(20vh)',
                minHeight: '100vh',
            }}
        >
            <ReadingForm token={token} />
        </Container>
    );
}
