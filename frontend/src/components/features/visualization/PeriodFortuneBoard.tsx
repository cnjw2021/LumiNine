import React from 'react';
import { Card, Text, Box, Tooltip, Group } from '@mantine/core';
import Image from 'next/image';
import { 
  IconArrowUp, 
  IconArrowDown, 
  IconArrowLeft, 
  IconArrowRight,
  IconArrowUpRight,
  IconArrowUpLeft,
  IconArrowDownRight,
  IconArrowDownLeft,
  IconAlertTriangle
} from '@tabler/icons-react';
import { HiCheckBadge } from 'react-icons/hi2';

// 日付をYYYY-MM-DD形式からM/D形式に変換
const formatDateJP = (dateStr: string, showYear: boolean = false): string => {
  if (!dateStr) return '';
  const [year, month, day] = dateStr.split('-');
  // 先頭の0を取り除く
  const formattedMonth = month.replace(/^0+/, '');
  const formattedDay = day.replace(/^0+/, '');
  
  return showYear 
    ? `${year}年${formattedMonth}月${formattedDay}日` 
    : `${formattedMonth}/${formattedDay}`;
};

// 方位の運気情報の型定義
interface DirectionDetails {
  is_auspicious: boolean;
  marks: string[];
  reason: string | null;
  is_main_star?: boolean;
  title?: string;
  details?: string;
}

// 期間（年・月）ごとの運気盤面データの型定義
interface PeriodFortuneData {
  center_star: number;
  display_month: string;
  display_year?: string;
  month: number;
  year: number;
  zodiac: string;
  directions: Record<string, DirectionDetails>;
  period_start?: string;
  period_end?: string;
}

interface PeriodFortuneBoardProps {
  periodData: PeriodFortuneData;
}

const PeriodFortuneBoard: React.FC<PeriodFortuneBoardProps> = ({ periodData }) => {
  const { center_star, display_month, display_year, period_start, period_end } = periodData;
  
  // SVGファイルのパスを生成
  const svgPath = `/images/main_star/${center_star}.svg`;
  
  // 期間表示（YYYY-MM-DD → M/D～M/D または YYYY年M月D日～YYYY年M月D日）
  const periodText = period_start && period_end 
    ? periodData.month === 0 
      ? `(${formatDateJP(period_start, true)} ～ ${formatDateJP(period_end, true)})` // 年データの場合
      : `(${formatDateJP(period_start)} ～ ${formatDateJP(period_end)})` // 月データの場合
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

  // 本命星の方位と情報を抽出
  const mainStarDirection = Object.entries(periodData.directions).find(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    ([_, data]) => data.is_main_star
  );
  
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
          {display_year} {display_month} <Text component="span" size="sm" c="dimmed" style={{ whiteSpace: 'nowrap', fontWeight: 'normal' }}>{periodText}</Text>
        </Text>
      </div>
      
      {/* 本命星の情報表示 */}
      {mainStarDirection && (
        <Group mt="xs" mb="sm" style={{ 
          background: 'rgba(255, 255, 255, 0.8)', 
          padding: '10px 12px', 
          borderRadius: '8px',
          border: '1px solid rgba(0, 150, 136, 0.2)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
          flex: '0 0 auto'
        }}>
          <Box style={{ 
            width: '28px', 
            height: '28px', 
            borderRadius: '50%', 
            backgroundColor: mainStarDirection[1].is_auspicious 
              ? 'rgba(0, 150, 136, 0.1)' 
              : 'rgba(255, 152, 0, 0.1)',
            border: mainStarDirection[1].is_auspicious 
              ? '2px solid rgba(0, 150, 136, 0.8)' 
              : '2px solid #ff9800',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '12px'
          }}>
            {/* 方位に対応するアイコンを表示 */}
            {(() => {
              // 方位と吉凶判定を取得
              const directionData = mainStarDirection[1];
              const isAuspicious = directionData.is_auspicious;
              const iconColor = isAuspicious ? 'rgba(0, 150, 136, 0.9)' : '#ff5722'; // 吉凶に応じてアイコンの色を変更
              
              switch(mainStarDirection[0]) {
                case 'north': return <IconArrowDown size={28} color={iconColor} />;
                case 'south': return <IconArrowUp size={28} color={iconColor} />;
                case 'east': return <IconArrowLeft size={28} color={iconColor} />;
                case 'west': return <IconArrowRight size={28} color={iconColor} />;
                case 'northeast': return <IconArrowDownLeft size={28} color={iconColor} />;
                case 'northwest': return <IconArrowDownRight size={28} color={iconColor} />;
                case 'southeast': return <IconArrowUpLeft size={28} color={iconColor} />;
                case 'southwest': return <IconArrowUpRight size={28} color={iconColor} />;
                case 'center': return <span style={{ fontSize: '14px', color: iconColor }}>中</span>;
                default: return null;
              }
            })()}
          </Box>
          <Box style={{ flex: 1 }}>
            <Text fw={600} size="sm" c={mainStarDirection[1].is_auspicious ? "teal.8" : "orange.8"}>
              {mainStarDirection[1].title || "本命星"}
            </Text>
            {mainStarDirection[1].details && (
              <Text size="xs" c="gray.7" style={{ 
                minHeight: '50px',
                maxHeight: '70px',
                overflow: 'auto'
              }}>
                {mainStarDirection[1].details}
              </Text>
            )}
          </Box>
        </Group>
      )}
      
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
            alt={`${display_year} ${display_month}の九星盤`}
            fill
            style={{ objectFit: 'contain', opacity: 0.9 }}
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
              {/* 中央（中心） */}
              {periodData.directions.center && (
                <Box style={{ 
                  position: 'absolute', 
                  top: '33%', 
                  left: '33%', 
                  width: '33%', 
                  height: '33%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.center.is_main_star && (
                    <>
                      {periodData.directions.center.is_auspicious ? (
                        <Tooltip label={periodData.directions.center.title || "本命星（中央）"} position="top">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.center.title || "注意（中央）"} position="top">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 24 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
              
              {/* 北（下）270° */}
              {periodData.directions.north && (
                <Box style={{ 
                  position: 'absolute', 
                  top: 'calc(50% + 62% - 8%)', 
                  left: 'calc(50% - 8%)', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.north.is_main_star && (
                    <>
                      {periodData.directions.north.is_auspicious ? (
                        <Tooltip label={periodData.directions.north.title || "本命星"} position="bottom">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.north.title || "注意"} position="bottom">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 24 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
              
              {/* 南（上）90° */}
              {periodData.directions.south && (
                <Box style={{ 
                  position: 'absolute', 
                  top: 'calc(50% - 62% - 8%)', 
                  left: 'calc(50% - 8%)', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.south.is_main_star && (
                    <>
                      {periodData.directions.south.is_auspicious ? (
                        <Tooltip label={periodData.directions.south.title || "本命星"} position="top">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.south.title || "注意"} position="top">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 24 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
              
              {/* 東（左）0° */}
              {periodData.directions.east && (
                <Box style={{ 
                  position: 'absolute', 
                  top: 'calc(50% - 8%)', 
                  left: 'calc(50% - 62% - 8%)', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.east.is_main_star && (
                    <>
                      {periodData.directions.east.is_auspicious ? (
                        <Tooltip label={periodData.directions.east.title || "本命星"} position="left">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.east.title || "注意"} position="left">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 24 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
              
              {/* 西（右）180° */}
              {periodData.directions.west && (
                <Box style={{ 
                  position: 'absolute', 
                  top: 'calc(50% - 8%)', 
                  left: 'calc(50% + 62% - 8%)', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.west.is_main_star && (
                    <>
                      {periodData.directions.west.is_auspicious ? (
                        <Tooltip label={periodData.directions.west.title || "本命星"} position="right">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.west.title || "注意"} position="right">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 24 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
              
              {/* 北東（左下）315° */}
              {periodData.directions.northeast && (
                <Box style={{ 
                  position: 'absolute', 
                  top: 'calc(50% + 44% - 8%)', 
                  left: 'calc(50% - 44% - 8%)', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.northeast.is_main_star && (
                    <>
                      {periodData.directions.northeast.is_auspicious ? (
                        <Tooltip label={periodData.directions.northeast.title || "本命星"} position="bottom-start">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.northeast.title || "注意"} position="bottom-start">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 24 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
              
              {/* 北西（右下）225° */}
              {periodData.directions.northwest && (
                <Box style={{ 
                  position: 'absolute', 
                  top: 'calc(50% + 44% - 8%)', 
                  left: 'calc(50% + 44% - 8%)', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.northwest.is_main_star && (
                    <>
                      {periodData.directions.northwest.is_auspicious ? (
                        <Tooltip label={periodData.directions.northwest.title || "本命星"} position="bottom-end">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.northwest.title || "注意"} position="bottom-end">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 24 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
              
              {/* 南東（左上）45° */}
              {periodData.directions.southeast && (
                <Box style={{ 
                  position: 'absolute', 
                  top: 'calc(50% - 44% - 8%)', 
                  left: 'calc(50% - 44% - 8%)', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.southeast.is_main_star && (
                    <>
                      {periodData.directions.southeast.is_auspicious ? (
                        <Tooltip label={periodData.directions.southeast.title || "本命星"} position="top-start">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.southeast.title || "注意"} position="top-start">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 24 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
              
              {/* 南西（右上）135° */}
              {periodData.directions.southwest && (
                <Box style={{ 
                  position: 'absolute', 
                  top: 'calc(50% - 44% - 8%)', 
                  left: 'calc(50% + 44% - 8%)', 
                  width: '16%', 
                  height: '16%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 6
                }}>
                  {periodData.directions.southwest.is_main_star && (
                    <>
                      {periodData.directions.southwest.is_auspicious ? (
                        <Tooltip label={periodData.directions.southwest.title || "本命星"} position="top-end">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <HiCheckBadge size={window.innerWidth <= 768 ? 24 : 36} color="#667eea" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      ) : (
                        <Tooltip label={periodData.directions.southwest.title || "注意"} position="top-end">
                          <div style={{ 
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}>
                            <IconAlertTriangle size={window.innerWidth <= 768 ? 28 : 36} color="#ff5722" style={{ 
                              filter: 'drop-shadow(0 2px 4px rgba(255, 87, 34, 0.3))'
                            }} />
                          </div>
                        </Tooltip>
                      )}
                    </>
                  )}
                </Box>
              )}
            </Box>
          </div>
        </div>
      </Box>
    </Card>
  );
};

export default PeriodFortuneBoard; 