"use client";

import React from "react";
import { Container, Title, Text, Stack, Card } from "@mantine/core";

export default function NineStarKiPage() {
    return (
        <Container size="md" py="xl">
            <Stack gap="lg">
                <Title order={1} c="#4BA3E3">九星気学について</Title>
                <Card withBorder shadow="sm" radius="md" p="xl">
                    <Text size="lg" mb="md">
                        九星気学（Nine Star Ki）は、生年月日から導き出される九星と、それぞれの星が持つ「気」の性質を用いて、運勢や方位の吉凶を占う東洋の占術です。
                    </Text>
                    <Text>
                        ベースの性質を表す本命星、行動パターンを表す月命星などを計算し、年運、月運、そして吉方位・凶方位を導き出します。
                    </Text>
                </Card>
            </Stack>
        </Container>
    );
}
