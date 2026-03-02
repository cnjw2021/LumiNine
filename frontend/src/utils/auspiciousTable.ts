import { MovingDateInfo, WaterDrawingDateInfo } from '@/types/directionFortune';

export interface MonthDirectionGroup {
  direction: string;
  dates: (MovingDateInfo | WaterDrawingDateInfo)[];
}

export interface MonthGroup {
  year: number;
  month: number;
  directions: MonthDirectionGroup[];
}

export const groupDatesByMonthAndDirection = (
  dateList: (MovingDateInfo | WaterDrawingDateInfo)[],
  directionOrder: string[]
): MonthGroup[] => {
  const monthMap = new Map<string, MonthGroup>();
  dateList.forEach((item) => {
    const dateObj = new Date(item.date);
    const year = dateObj.getFullYear();
    const month = dateObj.getMonth() + 1;
    const key = `${year}-${month}`;
    if (!monthMap.has(key)) {
      monthMap.set(key, { year, month, directions: [] });
    }
    const monthGroup = monthMap.get(key)!;
    item.auspicious_directions.forEach((direction) => {
      let dirGroup = monthGroup.directions.find((d) => d.direction === direction);
      if (!dirGroup) {
        dirGroup = { direction, dates: [] };
        monthGroup.directions.push(dirGroup);
      }
      dirGroup.dates.push(item);
    });
  });

  return Array.from(monthMap.values())
    .map((group) => ({
      ...group,
      directions: group.directions
        .map((dirGroup) => ({
          ...dirGroup,
          dates: dirGroup.dates.sort((a, b) => a.date.localeCompare(b.date)),
        }))
        .sort((a, b) => {
          const aIdx = directionOrder.indexOf(a.direction);
          const bIdx = directionOrder.indexOf(b.direction);
          if (aIdx === -1 && bIdx === -1) return a.direction.localeCompare(b.direction);
          if (aIdx === -1) return 1;
          if (bIdx === -1) return -1;
          return aIdx - bIdx;
        }),
    }))
    .sort((a, b) => a.year - b.year || a.month - b.month);
};

export const formatDays = (items: (MovingDateInfo | WaterDrawingDateInfo)[]) => {
  const days = items
    .map((item) => new Date(item.date).getDate())
    .sort((a, b) => a - b);
  return days.map((day) => `${day}日`).join(', ');
};

export const formatWaterDays = (items: (MovingDateInfo | WaterDrawingDateInfo)[]) => {
  return items
    .map((item) => {
      const day = new Date(item.date).getDate();
      const time = 'auspicious_times' in item && item.auspicious_times && item.auspicious_times.length > 0
        ? item.auspicious_times[0].time
        : '';
      return time ? `${day}日(${time})` : `${day}日`;
    })
    .join(', ');
};
