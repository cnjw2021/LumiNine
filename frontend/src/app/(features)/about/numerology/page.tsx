"use client";

import React from "react";
import { Container, Title, Text, Stack, Card } from "@mantine/core";

export default function NumerologyPage() {
    return (
        <Container size="md" py="xl">
            <Stack gap="lg">
                <Title order={1} c="#4BA3E3">数秘術について</Title>
                <Card withBorder shadow="sm" radius="md" p="xl">
                    <Text size="lg" mb="md">
                        数秘術（Numerology）は、生年月日や姓名から導き出される数字を用いて、個人の性格、才能、運命などを読み解く占術です。
                    </Text>
                    <Text>
                        LumiNineでは、生年月日からライフパスナンバーなどの重要な数字を計算し、あなたに最適なパワーストーンやアドバイスを提供します。
                    </Text>
                </Card>
            </Stack>
        </Container>
    );
}
