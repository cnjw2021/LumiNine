import React from 'react';
import { Card, Title, Text, Stack, Group, rem } from '@mantine/core';
import { generateFiveElementsCycleSVG } from '@/utils/fiveElementsCycleSVG';

interface FiveElementsCycleProps {
  size?: number;
}

const FiveElementsCycle: React.FC<FiveElementsCycleProps> = ({ size = 600 }) => {
  return (
    <Stack gap={rem(32)}>
      <Card 
        shadow="md" 
        p="xl" 
        radius="sm" 
        withBorder
        style={{ 
          marginBottom: '1.5rem',
          background: 'linear-gradient(145deg, white, #f0f2f5)',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <div style={{ position: 'relative', zIndex: 1 }}>
          <Title 
            order={3} 
            style={{
              textAlign: 'center',
              marginBottom: '20px',
              fontSize: '1.4rem',
              fontWeight: 600,
              color: '#333'
            }}
          >
            五行相関図
          </Title>

          <Text size="sm" mb="lg" style={{ textAlign: 'justify' }}>
            九星気学の根幹をなす「五行思想」は、自然界のすべての事象を5つの要素で説明する東洋哲学の考え方です。「木（もく）」「火（か）」「土（ど）」「金（ごん）」「水（すい）」という5つの要素が互いに影響を与え合い、バランスを保ちながら循環することで、世界が成り立っているとされています。
          </Text>

          <div 
            style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              padding: '1rem'
            }}
            dangerouslySetInnerHTML={{ 
              __html: generateFiveElementsCycleSVG(size) 
            }} 
          />

          <Text size="sm" mt="lg" style={{ textAlign: 'justify' }}>
            この図は、五行の要素間の関係性を表しています。外側を巡る矢印は相手を育む「相生（そうじょう）」の関係を、中央の星形を描く矢印は相手を抑制する「相剋（そうこく）」の関係を示しています。また、同じ要素同士には「比和（ひわ）」という特別な関係性があります。
          </Text>
        </div>
      </Card>

      <Card shadow="md" p="xl" radius="sm" withBorder>
        <Title 
          order={3} 
          style={{
            textAlign: 'center',
            marginBottom: '20px',
            fontSize: '1.4rem',
            fontWeight: 600,
            color: '#333'
          }}
        >
          五行の相性と運気の流れ
        </Title>

        <Text size="sm" mb="xl" style={{ textAlign: 'justify' }}>
          これらの要素間の関係性を理解することは、ご自身の本命星が持つ性質や、他の星との相性を読み解く重要な鍵となります。それぞれの関係性について、詳しく見ていきましょう。
        </Text>

        <Stack gap={rem(32)}>
          {/* 相生の関係 */}
          <div>
            <Group gap={rem(8)} mb="md">
              <svg className="relationship-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M5 21c.5 -4.5 2.5 -8 7 -10" stroke="#4CAF50" strokeWidth="1.5"/>
                <path d="M9 18c6.218 0 10.5 -3.288 11 -12v-2h-4.014c-9 0 -11.986 4 -12 9c0 1 0 3 2 5h3z" stroke="#4CAF50" strokeWidth="1.5"/>
              </svg>
              <Title order={4} style={{ color: '#333' }}>
                互いを助け、育む「相生（そうじょう）」の関係
              </Title>
            </Group>
            <Text size="sm" mb="md" style={{ textAlign: 'justify' }}>
              図の外側を巡る矢印は、一方の気がもう一方を生み出し、その力を強める良好な関係を示します。例えば、水は木を育て、木は火を生み出すというように、要素同士が互いに支え合う関係です。これを「相生（そうじょう）」と呼び、幸運や発展をもたらす理想的な相性です。
            </Text>
            <Text size="sm" style={{ textAlign: 'justify' }}>
              相生の関係にある相手は、あなたを理解し、サポートしてくれる存在です。一緒にいると物事がスムーズに進んだり、お互いの長所を引き出し合えたりするでしょう。
            </Text>
          </div>

          {/* 相剋の関係 */}
          <div>
            <Group gap={rem(8)} mb="md">
              <svg className="relationship-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0" stroke="#FF5722" strokeWidth="1.5"/>
                <path d="M12 3a4.5 4.5 0 0 0 0 9a4.5 4.5 0 0 1 0 9" stroke="#FF5722" strokeWidth="1.5"/>
                <circle cx="12" cy="7.5" r=".5" fill="#FF5722"/>
                <circle cx="12" cy="16.5" r=".5" fill="#FF5722"/>
              </svg>
              <Title order={4} style={{ color: '#333' }}>
                相手を抑制し、試練を与える「相剋（そうこく）」の関係
              </Title>
            </Group>
            <Text size="sm" mb="md" style={{ textAlign: 'justify' }}>
              図の中央で星形を描く矢印は、一方の気がもう一方を抑制する関係を示します。例えば、水は火を消し、火は金を溶かすというように、要素同士が互いに制御し合う関係です。これを「相剋（そうこく）」と呼び、時として対立や困難を生みやすい緊張感のある相性です。
            </Text>
            <Text size="sm" style={{ textAlign: 'justify' }}>
              相剋の相手とは、意見がぶつかったり、気疲れしやすかったりするかもしれません。しかし、この関係は必ずしもマイナスではありません。相手の存在が自分にない視点や成長の機会を与えてくれることもあります。相手の性質を理解し、適切な距離感を保つことが、良い関係を築く鍵となります。
            </Text>
          </div>

          {/* 比和の関係 */}
          <div>
            <Group gap={rem(8)} mb="md">
              <svg className="relationship-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                {/* 左側の星 */}
                <path d="M4 10L7.5 9.5L9 6L10.5 9.5L14 10L11 12L12 15.5L9 13.5L6 15.5L7 12L4 10Z" fill="#9C27B0"/>
                {/* 右上の星 */}
                <path d="M12 3L15.5 2.5L17 0L18.5 2.5L22 3L19 5L20 8.5L17 6.5L14 8.5L15 5L12 3Z" fill="#9C27B0"/>
                {/* 右下の星 */}
                <path d="M12 15L15.5 14.5L17 12L18.5 14.5L22 15L19 17L20 20.5L17 18.5L14 20.5L15 17L12 15Z" fill="#9C27B0"/>
              </svg>
              <Title order={4} style={{ color: '#333' }}>
                同じ性質を持つ「比和（ひわ）」の関係
              </Title>
            </Group>
            <Text size="sm" style={{ textAlign: 'justify' }}>
              同じ五行の性質を持つ星同士（例：三碧木星と四緑木星）の関係を「比和（ひわ）」と呼びます。同じ性質を持つため、価値観や考え方が似ており、仲間意識が強く、すぐに意気投合できる良い相性です。ただし、似た者同士ゆえに、お互いの短所も強め合ってしまうことがあるため、時には異なる視点を取り入れることも大切です。
            </Text>
          </div>
        </Stack>
      </Card>
    </Stack>
  );
};

export default FiveElementsCycle;