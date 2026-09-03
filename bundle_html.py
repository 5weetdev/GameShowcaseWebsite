import argparse
import base64
import json
import mimetypes
import os
import re
import sys

VIDEO_FACADE_CSS = """
/* --- Video Facade (Lazy Thumbnail Player for Standalone HTML) --- */
.video-facade {
    position: relative;
    width: 100%;
    cursor: pointer;
    background-color: #000;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}
.featured-card-media .video-facade {
    width: 100%;
    height: 100%;
    aspect-ratio: 16 / 9;
}
.hypercasual-card .video-facade {
    width: 100%;
    aspect-ratio: 9 / 16;
}
.video-card .video-facade {
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: 8px;
    margin-bottom: 1rem;
}
.video-facade-thumb {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.3s ease, filter 0.3s ease;
}
.video-facade:hover .video-facade-thumb {
    transform: scale(1.04);
    filter: brightness(1.1);
}
.video-facade-play {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 60px;
    height: 42px;
    pointer-events: none;
    transition: transform 0.2s ease, filter 0.2s ease;
    z-index: 2;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.6));
}
.video-facade:hover .video-facade-play {
    transform: translate(-50%, -50%) scale(1.18);
}
.video-facade-badge {
    position: absolute;
    bottom: 8px;
    right: 8px;
    background: rgba(10, 15, 20, 0.85);
    color: #e6f1ff;
    font-size: 0.75rem;
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 4px;
    pointer-events: none;
    z-index: 2;
}
.video-facade:hover .video-facade-badge {
    border-color: var(--primary-color);
    color: #fff;
}
"""

VIDEO_FACADE_JS = r"""
            function extractYouTubeId(url) {
                if (!url) return '';
                const match = url.match(/(?:embed\/|v=|vi\/|youtu\.be\/|\/v\/|shorts\/)([^?&"/]+)/);
                return match ? match[1] : '';
            }

            function createVideoFacade(embedUrl, title, isVertical = false) {
                const videoId = extractYouTubeId(embedUrl);
                if (!videoId) return '';
                const thumbUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
                const isFile = window.location.protocol === 'file:';
                const actionLabel = isFile ? 'Watch on YouTube ↗' : 'Play Video';

                return `
                    <div class="video-facade" data-video-id="${videoId}" onclick="playVideoFacade(this, '${videoId}', ${isVertical})" title="${title}">
                        <img src="${thumbUrl}" alt="${title}" class="video-facade-thumb" loading="lazy">
                        <svg class="video-facade-play" viewBox="0 0 68 48">
                            <path d="M66.52,7.74c-0.78-2.93-2.49-5.41-5.42-6.19C55.79,.13,34,0,34,0S12.21,.13,6.9,1.55 C3.97,2.33,2.27,4.81,1.48,7.74C0.06,13.05,0,24,0,24s0.06,10.95,1.48,16.26c0.78,2.93,2.49,5.41,5.42,6.19 C12.21,47.87,34,48,34,48s21.79-0.13,27.1-1.55c2.93-0.78,4.64-3.26,5.42-6.19C67.94,34.95,68,24,68,24S67.94,13.05,66.52,7.74z" fill="#ff0000" fill-opacity="0.9"></path>
                            <path d="M 45,24 27,14 27,34" fill="#ffffff"></path>
                        </svg>
                        <span class="video-facade-badge">${actionLabel}</span>
                    </div>`;
            }

            window.playVideoFacade = function(container, videoId, isVertical) {
                // When opened via file:// protocol, YouTube's embedded player blocks playback
                // and throws Error 153 due to missing HTTP Referer/Origin headers.
                // In file:// mode, open the video directly on YouTube in a new tab for seamless playback!
                if (window.location.protocol === 'file:') {
                    window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank', 'noopener,noreferrer');
                    return;
                }

                // When hosted on web servers (http/https), dynamically embed and autoplay in-place
                const iframe = document.createElement('iframe');
                iframe.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0`;
                iframe.title = "YouTube video player";
                iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
                iframe.allowFullscreen = true;
                iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
                iframe.style.width = '100%';
                iframe.style.height = '100%';
                iframe.style.border = 'none';
                iframe.style.display = 'block';
                if (isVertical) {
                    iframe.style.aspectRatio = '9 / 16';
                } else {
                    iframe.style.aspectRatio = '16 / 9';
                }

                container.innerHTML = '';
                container.style.cursor = 'default';
                container.onclick = null;
                container.appendChild(iframe);
            };
"""

def get_data_uri(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.webp':
            mime_type = 'image/webp'
        elif ext == '.svg':
            mime_type = 'image/svg+xml'
        else:
            mime_type = 'application/octet-stream'
    
    with open(file_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return f"data:{mime_type};base64,{encoded}"

def inline_data_object(obj, base_dir, stats):
    if isinstance(obj, str):
        clean_path = obj.strip()
        local_path = os.path.normpath(os.path.join(base_dir, clean_path))
        if os.path.isfile(local_path) and any(clean_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.ico']):
            data_uri = get_data_uri(local_path)
            stats['inlined_images'] += 1
            return data_uri
        return obj
    elif isinstance(obj, list):
        return [inline_data_object(item, base_dir, stats) for item in obj]
    elif isinstance(obj, dict):
        return {k: inline_data_object(v, base_dir, stats) for k, v in obj.items()}
    return obj

def build_standalone_html(input_html="index.html", output_html="portfolio.html"):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    html_path = os.path.join(base_dir, input_html)
    output_path = os.path.join(base_dir, output_html)

    if not os.path.isfile(html_path):
        raise FileNotFoundError(f"Input HTML file not found: {html_path}")

    stats = {'inlined_images': 0}
    print(f"[+] Reading {html_path} (original source stays untouched)...")
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Inline favicon
    icon_match = re.search(r'<link\s+rel=["\']icon["\']\s+type=["\'][^"\']*["\']\s+href=["\']([^"\']+)["\']', html)
    if icon_match:
        icon_rel_path = icon_match.group(1)
        icon_full_path = os.path.join(base_dir, icon_rel_path)
        if os.path.isfile(icon_full_path):
            icon_uri = get_data_uri(icon_full_path)
            html = html.replace(icon_match.group(0), f'<link rel="icon" href="{icon_uri}"')
            stats['inlined_images'] += 1
            print(f"[+] Inlined favicon: {icon_rel_path}")

    # 2. Inline styles.css + append Video Facade styles
    css_match = re.search(r'<link\s+rel=["\']stylesheet["\']\s+href=["\']([^"\']+)["\']\s*/?>', html)
    if css_match:
        css_rel_path = css_match.group(1)
        css_full_path = os.path.join(base_dir, css_rel_path)
        if os.path.isfile(css_full_path):
            with open(css_full_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            style_tag = f"<style>\n{css_content}\n{VIDEO_FACADE_CSS}\n</style>"
            html = html.replace(css_match.group(0), style_tag)
            print(f"[+] Inlined stylesheet: {css_rel_path} with lazy video player styles")

    # 3. Read and inline portfolio-data.json
    json_path = os.path.join(base_dir, "portfolio-data.json")
    if os.path.isfile(json_path):
        print("[+] Processing portfolio-data.json and encoding images into Base64 Data URIs...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data = inline_data_object(data, base_dir, stats)
        inlined_json_str = json.dumps(data, ensure_ascii=False)

        # 4. Replace fetch('portfolio-data.json') logic with direct inline data & inject facade helpers
        fetch_pattern = re.compile(
            r"fetch\(['\"]portfolio-data\.json['\"]\).*?\.catch\(.*?\);",
            re.DOTALL
        )

        replacement = f"""{VIDEO_FACADE_JS}

            const data = {inlined_json_str};
            populatePage(data);
            setupImages();"""

        if fetch_pattern.search(html):
            html = fetch_pattern.sub(replacement, html, count=1)
            print("[+] Successfully replaced fetch('portfolio-data.json') with inlined data structure & video helpers.")
        else:
            raise RuntimeError("Could not find fetch('portfolio-data.json') block in index.html to replace.")

    # 5. Transform iframe constructions to use createVideoFacade
    # Featured iframe
    old_featured = 'mediaHTML = `<iframe src="${p.youtubeEmbedUrl}" title="${p.title} Video" allowfullscreen></iframe>`;'
    new_featured = 'mediaHTML = createVideoFacade(p.youtubeEmbedUrl, p.title, false);'
    if old_featured in html:
        html = html.replace(old_featured, new_featured)
        print("[+] Replaced featured projects iframe with video facade.")

    # Hypercasual iframe
    old_hyper = 'mediaHTML = `<iframe src="${p.youtubeEmbedUrl}" title="${p.title}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`;'
    new_hyper = 'mediaHTML = createVideoFacade(p.youtubeEmbedUrl, p.title, true);'
    if old_hyper in html:
        html = html.replace(old_hyper, new_hyper)
        print("[+] Replaced hypercasual projects iframe with video facade.")

    # Videos & Prototypes iframe (including fixing typo in original </p</div>)
    old_video_grid = 'videosGrid.innerHTML += `<div class="video-card"><h3>${p.title}</h3><iframe src="${p.youtubeEmbedUrl}" title="YouTube video player" allowfullscreen></iframe><p>${p.description}</p</div>`;'
    new_video_grid = 'videosGrid.innerHTML += `<div class="video-card"><h3>${p.title}</h3>${createVideoFacade(p.youtubeEmbedUrl, p.title, false)}<p>${p.description}</p></div>`;'
    if old_video_grid in html:
        html = html.replace(old_video_grid, new_video_grid)
        print("[+] Replaced videos grid iframe with video facade.")

    # 6. Write output file
    print(f"[+] Writing rendered standalone HTML to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[SUCCESS] Standalone HTML bundle created: {output_path}")
    print(f"          Original files unchanged: index.html, styles.css")
    print(f"          Total inlined images: {stats['inlined_images']}")
    print(f"          File size: {size_mb:.2f} MB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bundle website into a single standalone offline HTML file.")
    parser.add_argument("--input", default="index.html", help="Input HTML file (default: index.html)")
    parser.add_argument("--output", default="portfolio.html", help="Output single HTML file (default: portfolio.html)")
    args = parser.parse_args()

    build_standalone_html(input_html=args.input, output_html=args.output)
