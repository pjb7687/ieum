import satori from 'satori';
import { Resvg } from '@resvg/resvg-js';
import sharp from 'sharp';
import { readFileSync } from 'fs';
import { join } from 'path';
import { get } from '$lib/fetch';

const WIDTH = 1200;
const HEIGHT = 630;

// Cached resources (loaded once at module level)
let fontData = null;
let bgBase64 = null;
let logoBase64 = null;

function getStaticPath(filename) {
    // Try development path first, then production
    const paths = [
        join(process.cwd(), 'static', filename),
        join(process.cwd(), 'build', 'client', filename),
    ];
    for (const p of paths) {
        try {
            return readFileSync(p);
        } catch {}
    }
    throw new Error(`Static file not found: ${filename}`);
}

async function initResources() {
    if (fontData && bgBase64 && logoBase64) return;

    // Load font
    fontData = getStaticPath('fonts/NotoSansKR-Bold.ttf');

    // Convert webp images to PNG base64 (resvg doesn't support webp)
    const bgBuffer = getStaticPath('bg-events.webp');
    const bgPng = await sharp(bgBuffer).resize(WIDTH, HEIGHT).png().toBuffer();
    bgBase64 = 'data:image/png;base64,' + bgPng.toString('base64');

    const logoBuffer = getStaticPath('logo.webp');
    const logoPng = await sharp(logoBuffer).png().toBuffer();
    logoBase64 = 'data:image/png;base64,' + logoPng.toString('base64');
}

export async function GET({ url }) {
    await initResources();

    const pageUrl = url.searchParams.get('url') || '';

    // Fetch site name from API
    let siteName = 'IEUM';
    try {
        const response = await get('api/site-settings');
        if (response.ok && response.status === 200) {
            siteName = response.data.site_name || 'IEUM';
        }
    } catch {}

    // If the URL is an event page, fetch the event name
    let displayTitle = siteName;
    const eventMatch = pageUrl.match(/\/event\/(\d+)/);
    if (eventMatch) {
        try {
            const eventResponse = await get(`api/event/${eventMatch[1]}`);
            if (eventResponse.ok && eventResponse.status === 200) {
                displayTitle = eventResponse.data.name;
            }
        } catch {}
    }

    const element = {
        type: 'div',
        props: {
            style: {
                width: WIDTH,
                height: HEIGHT,
                display: 'flex',
                position: 'relative',
            },
            children: [
                // Background image
                {
                    type: 'img',
                    props: {
                        src: bgBase64,
                        width: WIDTH,
                        height: HEIGHT,
                        style: {
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: WIDTH,
                            height: HEIGHT,
                            objectFit: 'cover',
                        },
                    },
                },
                // Dark overlay
                {
                    type: 'div',
                    props: {
                        style: {
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: WIDTH,
                            height: HEIGHT,
                            backgroundColor: 'rgba(15, 23, 42, 0.65)',
                        },
                    },
                },
                // Content container
                {
                    type: 'div',
                    props: {
                        style: {
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: WIDTH,
                            height: HEIGHT,
                            display: 'flex',
                            flexDirection: 'column',
                            padding: '48px 64px',
                        },
                        children: [
                            // Logo (top-left)
                            {
                                type: 'img',
                                props: {
                                    src: logoBase64,
                                    height: 60,
                                    style: {
                                        height: 60,
                                        objectFit: 'contain',
                                        alignSelf: 'flex-start',
                                    },
                                },
                            },
                            // Site name (center)
                            {
                                type: 'div',
                                props: {
                                    style: {
                                        flex: 1,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    },
                                    children: {
                                        type: 'div',
                                        props: {
                                            style: {
                                                color: 'white',
                                                fontSize: 64,
                                                fontWeight: 700,
                                                textAlign: 'center',
                                                lineHeight: 1.2,
                                            },
                                            children: displayTitle,
                                        },
                                    },
                                },
                            },
                            // URL (bottom)
                            {
                                type: 'div',
                                props: {
                                    style: {
                                        color: 'rgba(255, 255, 255, 0.6)',
                                        fontSize: 22,
                                        textAlign: 'center',
                                    },
                                    children: pageUrl,
                                },
                            },
                        ],
                    },
                },
            ],
        },
    };

    const svg = await satori(element, {
        width: WIDTH,
        height: HEIGHT,
        fonts: [
            {
                name: 'NotoSansKR',
                data: fontData,
                weight: 700,
                style: 'normal',
            },
        ],
    });

    const resvg = new Resvg(svg, {
        fitTo: { mode: 'width', value: WIDTH },
    });
    const pngData = resvg.render();
    const pngBuffer = pngData.asPng();

    return new Response(pngBuffer, {
        headers: {
            'Content-Type': 'image/png',
            'Cache-Control': 'public, max-age=3600',
        },
    });
}
