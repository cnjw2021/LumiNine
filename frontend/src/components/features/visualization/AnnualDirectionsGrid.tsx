import React from 'react';
import { Text, Card, Badge, Divider, Box } from '@mantine/core';
import Image from 'next/image';

// 日付をYYYY-MM-DD形式からM/D形式に変換
const formatDateJP = (dateStr: string): string => {
  if (!dateStr) return '';
  const [, month, day] = dateStr.split('-');
  // 先頭の0を取り除く
  const formattedMonth = month.replace(/^0+/, '');
  const formattedDay = day.replace(/^0+/, '');
  return `${formattedMonth}/${formattedDay}`;
};

interface DirectionStatus {
  is_auspicious: boolean;
  reason: string | null;
  marks: string[];
}

interface PeriodDirectionData {
  center_star: number;
  display_month: string;
  month: number;
  year: number;
  period_start?: string;  // 期間開始日
  period_end?: string;    // 期間終了日
  directions: Record<string, DirectionStatus>;
}

interface AnnualDirectionsGridProps {
  periodData: PeriodDirectionData;
}

const AnnualDirectionsGrid: React.FC<AnnualDirectionsGridProps> = ({ periodData }) => {
  // SVGファイルのパスを生成
  const svgPath = `/images/main_star/${periodData.center_star}.svg`;

  // 期間表示（YYYY-MM-DD → M/D～M/D）
  const periodText = periodData.period_start && periodData.period_end 
    ? `(${formatDateJP(periodData.period_start)} ～ ${formatDateJP(periodData.period_end)})`
    : '';

  // 季節に合わせた背景色を設定
  const getSeasonalColor = (month: number): string => {
    // 季節ごとの色調
    switch(month) {
      case 2:
      case 3: return 'linear-gradient(to bottom, rgba(255, 222, 235, 0.3), rgba(255, 255, 255, 0.5))'; // 春（薄桜色）
      case 4:
      case 5: return 'linear-gradient(to bottom, rgba(200, 240, 210, 0.3), rgba(255, 255, 255, 0.5))'; // 初夏（若葉色）
      case 6:
      case 7: return 'linear-gradient(to bottom, rgba(173, 216, 230, 0.3), rgba(255, 255, 255, 0.5))'; // 夏（水色）
      case 8:
      case 9: return 'linear-gradient(to bottom, rgba(255, 236, 179, 0.3), rgba(255, 255, 255, 0.5))'; // 秋（薄橙色）
      case 10:
      case 11: return 'linear-gradient(to bottom, rgba(210, 180, 140, 0.3), rgba(255, 255, 255, 0.5))'; // 晩秋（タン色）
      case 12:
      case 1: return 'linear-gradient(to bottom, rgba(220, 230, 240, 0.3), rgba(255, 255, 255, 0.5))'; // 冬（薄氷色）
      default: return 'white';
    }
  };

  return (
    <Card shadow="sm" withBorder p="md" style={{ 
      background: getSeasonalColor(periodData.month),
      position: 'relative',
      height: '100%',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div>
        <Text fw={700} size="lg" c="blue">
          {periodData.display_month} <Text component="span" size="sm" c="dimmed" style={{ whiteSpace: 'nowrap', fontWeight: 'normal' }}>{periodText}</Text>
        </Text>
      </div>
      
      {/* SVG画像表示 */}
      <Box style={{ 
        width: '100%', 
        maxWidth: '340px', 
        position: 'relative', 
        aspectRatio: '1/1', 
        height: 'auto',
        margin: '15px auto',
        flex: '1 1 auto'
      }}>
        <div style={{
          position: 'relative',
          width: '100%',
          height: 0,
          paddingBottom: '100%'
        }}>
          <Image
            src={svgPath}
            alt={`${periodData.display_month}の九星盤`}
            fill
            style={{ objectFit: 'contain', opacity: 0.8 }}
            priority
          />
          
          {/* 八方位の吉凶を表示 */}
          <div style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            width: '100%', 
            height: '100%', 
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 5
          }}>
            {/* 3×3のグリッドとして九星盤を表示 */}
            <Box style={{ width: '80%', height: '80%', position: 'relative' }}>
              {/* 北（下） */}
              {periodData.directions.north && (
                <Box style={{ 
                  position: 'absolute', 
                  bottom: '-15%', 
                  left: '42%', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.north.is_auspicious && (
                    <Badge size="sm" color="green">
                      吉
                    </Badge>
                  )}
                </Box>
              )}
              
              {/* 南（上） */}
              {periodData.directions.south && (
                <Box style={{ 
                  position: 'absolute', 
                  top: '-18%', 
                  left: '42%', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.south.is_auspicious && (
                    <Badge size="sm" color="green">
                      吉
                    </Badge>
                  )}
                </Box>
              )}
              
              {/* 東（左） */}
              {periodData.directions.east && (
                <Box style={{ 
                  position: 'absolute', 
                  top: '42%', 
                  left: '-18%', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.east.is_auspicious && (
                    <Badge size="sm" color="green">
                      吉
                    </Badge>
                  )}
                </Box>
              )}
              
              {/* 西（右） */}
              {periodData.directions.west && (
                <Box style={{ 
                  position: 'absolute', 
                  top: '42%', 
                  right: '-18%', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.west.is_auspicious && (
                    <Badge size="sm" color="green">
                      吉
                    </Badge>
                  )}
                </Box>
              )}
              
              {/* 北東（左下） */}
              {periodData.directions.northeast && (
                <Box style={{ 
                  position: 'absolute', 
                  bottom: '5%', 
                  left: '0%', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.northeast.is_auspicious && (
                    <Badge size="sm" color="green">
                      吉
                    </Badge>
                  )}
                </Box>
              )}
              
              {/* 北西（右下） */}
              {periodData.directions.northwest && (
                <Box style={{ 
                  position: 'absolute', 
                  bottom: '5%', 
                  right: '0%', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.northwest.is_auspicious && (
                    <Badge size="sm" color="green">
                      吉
                    </Badge>
                  )}
                </Box>
              )}
              
              {/* 南東（左上） */}
              {periodData.directions.southeast && (
                <Box style={{ 
                  position: 'absolute', 
                  top: '5%', 
                  left: '0%', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.southeast.is_auspicious && (
                    <Badge size="sm" color="green">
                      吉
                    </Badge>
                  )}
                </Box>
              )}
              
              {/* 南西（右上） */}
              {periodData.directions.southwest && (
                <Box style={{ 
                  position: 'absolute', 
                  top: '5%', 
                  right: '0%', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.southwest.is_auspicious && (
                    <Badge size="sm" color="green">
                      吉
                    </Badge>
                  )}
                </Box>
              )}
            </Box>
          </div>
        </div>
      </Box>
      
      <Divider my="sm" />
    </Card>
  );
};

export default AnnualDirectionsGrid; 