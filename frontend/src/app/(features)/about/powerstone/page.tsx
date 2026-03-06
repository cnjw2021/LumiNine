"use client";

import React from "react";
import { Container, Title, Text, Stack, Card } from "@mantine/core";

export default function PowerstonePage() {
    return (
        <Container size="md" py="xl">
            <Stack gap="lg">
                <Title order={1} c="#4BA3E3">パワーストーンについて</Title>
                <Card withBorder shadow="sm" radius="md" p="xl">
                    <Text size="lg" mb="md">
                        パワーストーンは、自然界のエネルギーを宿した天然石であり、身につける人の運気をサポートしたり、バランスを整えたりする力があるとされています。
                    </Text>
                    <Text>
                        LumiNineでは、数秘術と九星気学の複合的なアプローチを用いて、その時のあなたに最も必要なパワーストーンを多角的に選定します。
                    </Text>
                </Card>
            </Stack>
        </Container>
    );
}
