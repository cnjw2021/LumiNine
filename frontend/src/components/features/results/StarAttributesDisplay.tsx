'use client';

import React, { useState, useEffect } from 'react';
import { Paper, Stack, Badge, Text, Loader, Grid, Divider } from '@mantine/core';
import api from '@/utils/api';

// StarAttributeの型定義
interface StarAttribute {
  main_star: number;
  month_star?: number | null;
  attribute_type: string;
  attribute_value: string;
  description?: string;
  weight?: number;
}

// 属性タイプ名のマッピング
const attributeTypeLabels: Record<string, string> = {
  'color': '色',
  'place': '場所',
  'item': 'アイテム',
  'food': '食べ物',
  'direction': '方位',
  'season': '季節',
  'job': '適職',
  'animal': '動物',
  'body': '体',
  'person': '人物',
  'phenomenon': '現象',
  'plant': '植物',
  'shape': '形',
  'weather': '天気'
};

interface StarAttributesDisplayProps {
  mainStar: number;
  mainStarName?: string;
}

const StarAttributesDisplay: React.FC<StarAttributesDisplayProps> = ({ mainStar, mainStarName = '本命星' }) => {
  const [starAttributes, setStarAttributes] = useState<Record<string, StarAttribute[]>>({});
  const [attributesLoading, setAttributesLoading] = useState(true);

  // 属性情報を取得
  useEffect(() => {
    const fetchStarAttributes = async () => {
      if (!mainStar) return;
      
      try {
        setAttributesLoading(true);
        const response = await api.get(`/nine-star/star-attributes?star_number=${mainStar}`);
        
        if (response.data) {
          // 属性タイプごとにグループ化
          const groupedAttributes: Record<string, StarAttribute[]> = {};
          
          response.data.forEach((attr: StarAttribute) => {
            if (!groupedAttributes[attr.attribute_type]) {
              groupedAttributes[attr.attribute_type] = [];
            }
            groupedAttributes[attr.attribute_type].push(attr);
          });
          
          // ソート
          Object.keys(groupedAttributes).forEach(type => {
            groupedAttributes[type].sort((a, b) => {
              // weight値がある場合はそれでソート
              if (a.weight !== undefined && b.weight !== undefined) {
                return a.weight - b.weight;
              }
              // なければ値でソート
              return a.attribute_value.localeCompare(b.attribute_value);
            });
          });
          
          setStarAttributes(groupedAttributes);
        }
      } catch (error) {
        console.error('星の属性の取得中にエラーが発生しました:', error);
      } finally {
        setAttributesLoading(false);
      }
    };
    
    fetchStarAttributes();
  }, [mainStar]);

  // 配列をチャンクに分割するヘルパー関数
  const chunk = <T,>(array: T[], size: number): T[][] => {
    const chunked: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
      chunked.push(array.slice(i, i + size));
    }
    return chunked;
  };

  // 属性タイプごとに色を取得
  const getAttributeColor = (type: string): string => {
    const colorMap: Record<string, string> = {
      'color': 'blue',
      'place': 'green',
      'item': 'indigo',
      'food': 'pink',
      'direction': 'orange',
      'season': 'teal',
      'job': 'violet',
      'animal': 'grape',
      'body': 'gray',
      'person': 'cyan',
      'phenomenon': 'lime',
      'plant': 'green',
      'shape': 'yellow',
      'weather': 'blue'
    };
    return colorMap[type] || 'gray';
  };

  // 属性タイプを順序づけ（表示の優先順位）
  const sortedAttributeTypes = Object.keys(starAttributes).sort((a, b) => {
    const order: Record<string, number> = {
      'color': 1,
      'place': 2,
      'direction': 3,
      'item': 4,
      'food': 5,
      'season': 6,
      'job': 7
    };
    return (order[a] || 100) - (order[b] || 100);
  });

  return (
    <Paper shadow="sm" p="md" withBorder>
      <Stack gap="md">
        <h3 style={{fontSize: '1.4rem', textAlign: 'center', marginTop: 0, marginBottom: '15px', color: '#333'}}>
        {mainStarName}の属性
        </h3>
        
        {attributesLoading ? (
          <Stack align="center" py="md">
            <Loader size="sm" />
            <Text size="sm">属性情報を読み込み中...</Text>
          </Stack>
        ) : (
          <Stack gap="lg">
            {/* 属性タイプを画面サイズに応じて1、2、3列で表示 */}
            {chunk(sortedAttributeTypes, 3).map((typePair, pairIndex) => (
              <div key={pairIndex}>
                <Grid>
                  {typePair.map((type) => (
                    <Grid.Col key={type} span={{ base: 12, xs: 6, md: 4 }}>
                      <Badge 
                        size="md" 
                        color={getAttributeColor(type)} 
                        mb="sm"
                        style={{ marginLeft: 0 }}
                      >
                        {attributeTypeLabels[type] || type}
                      </Badge>
                      
                      <div style={{ 
                        display: 'flex', 
                        flexWrap: 'wrap', 
                        gap: '8px',
                        marginTop: '8px'
                      }}>
                        {starAttributes[type].map((attr, index) => (
                          <div
                            key={index}
                            style={{ 
                              backgroundColor: `var(--mantine-color-${getAttributeColor(type)}-0)`,
                              border: `1px solid var(--mantine-color-${getAttributeColor(type)}-2)`, 
                              borderRadius: '12px',
                              padding: '6px 12px',
                              flex: '1 0 auto',
                              minWidth: 'fit-content',
                              boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                            }}
                          >
                            <Text 
                              fw={500} 
                              ta="center" 
                              size="sm" 
                              style={{ 
                                color: `var(--mantine-color-${getAttributeColor(type)}-9)`,
                                whiteSpace: 'nowrap'
                              }}
                            >
                              {attr.attribute_value}
                            </Text>
                          </div>
                        ))}
                      </div>
                    </Grid.Col>
                  ))}
                </Grid>
                
                {pairIndex < Math.ceil(sortedAttributeTypes.length / 3) - 1 && (
                  <Divider 
                    my="lg" 
                    variant="dashed" 
                    color="gray.3"
                  />
                )}
              </div>
            ))}
          </Stack>
        )}
      </Stack>
    </Paper>
  );
};

export default StarAttributesDisplay; 