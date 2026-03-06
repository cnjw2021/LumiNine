/**
 * Powerstone image mapping utility.
 * Maps stone_id → public image path for all 30 registered stones.
 */

const STONE_IDS = [
    'amethyst', 'aquamarine', 'aventurine', 'blue_sapphire', 'blue_topaz',
    'carnelian', 'cats_eye', 'citrine', 'clear_quartz', 'diamond',
    'emerald', 'fluorite', 'garnet', 'green_aventurine', 'hessonite', 'jade',
    'labradorite', 'lapis_lazuli', 'moonstone', 'onyx', 'pearl', 'peridot',
    'red_coral', 'rose_quartz', 'ruby', 'smoky_quartz', 'sunstone',
    'tiger_eye', 'tigers_eye', 'turquoise', 'yellow_jasper', 'yellow_sapphire',
] as const;

type StoneId = typeof STONE_IDS[number];

const STONE_IMAGE_SET = new Set<string>(STONE_IDS);

/** Default placeholder when stone_id is unknown */
const FALLBACK_IMAGE = '/images/stones/clear_quartz.png';

/**
 * Get the public image path for a given stone_id.
 * Falls back to a generic crystal image for unknown IDs.
 */
export function getStoneImagePath(stoneId: string | undefined): string {
    if (!stoneId) return FALLBACK_IMAGE;
    if (STONE_IMAGE_SET.has(stoneId)) {
        return `/images/stones/${stoneId}.png`;
    }
    return FALLBACK_IMAGE;
}

export type { StoneId };
