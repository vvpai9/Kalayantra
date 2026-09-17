import QtQuick 2.15

// Pictorial Vedic birth/divisional chart renderer.
// Styles: "north" (diamond), "south" (fixed-sign 4x4 grid), "east" (mirrored grid).
// Inputs are rashi indices per planet, the ascendant rashi, per-planet
// markers (retrograde / combust) and per-planet colors.  The component is
// varga-agnostic: feed D1 or any divisional placement set.

Canvas {
    id: chart

    property string style: "north"
    property int ascRashi: 0
    property var signs: []        // length 9: planet index -> rashi index (0..11)
    property var markers: []      // length 9: { retro: bool, combust: bool }
    property var colors: []       // length 9: color string per planet
    property string langKey: "en"

    property var glyphs: {
        "en": ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"],
        "iast": ["Sūrya", "Candra", "Maṅgala", "Budha", "Guru", "Śukra", "Śani", "Rāhu", "Ketu"],
        "devanagari": ["सूर्य", "चन्द्र", "मङ्गल", "बुध", "गुरु", "शुक्र", "शनि", "राहु", "केतु"]
    }
    property var rashiGlyphs: {
        "en": ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"],
        "iast": ["Meṣa", "Vṛṣabha", "Mithuna", "Karkaṭa", "Siṁha", "Kanyā", "Tulā", "Vṛścika", "Dhanu", "Makara", "Kumbha", "Mīna"],
        "devanagari": ["मेष", "वृषभ", "मिथुन", "कर्कट", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]
    }
    property color lineColor: {
        if (chart.width < 1) return "#888888";
        return Qt.rgba(0.55, 0.55, 0.55, 1.0);
    }
    property color labelColor: "#aaaaaa"
    property color retroColor: "#3daee9"
    property color combustColor: "#e67e22"
    property color asciiMarkerColor: "#2ecc71"

    onStyleChanged: requestPaint()
    onAscRashiChanged: requestPaint()
    onSignsChanged: requestPaint()
    onMarkersChanged: requestPaint()
    onLangKeyChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()

    onPaint: {
        var ctx = getContext("2d");
        ctx.reset();
        ctx.clearRect(0, 0, width, height);

        if (style === "north") paintNorth(ctx);
        else if (style === "south") paintGrid(ctx, false);
        else paintGrid(ctx, true);
    }

    // ---------- shared helpers ----------

    function planetListForShip(ship) {
        var pts = [];
        for (var i = 0; i < signs.length && i < 9; i++) {
            if (signs[i] === ship) pts.push(i);
        }
        pts.sort(function(a, b) { return a - b; });
        return pts;
    }

    // Polygon of the cell for the given house position (North style, virtual
    // 320-space).  The North Indian chart is built from the outer square, the
    // inner diamond (L-T-R-B) and the two diagonals crossing at C; the twelve
    // cells are four central quadrilaterals and eight corner triangles.
    function northPoly(pos) {
        var TL = [18, 18], T = [160, 18], TR = [302, 18], R = [302, 160];
        var BR = [302, 302], B = [160, 302], BL = [18, 302], L = [18, 160];
        var a = [89, 89], b = [231, 89], c = [231, 231], d = [89, 231], C = [160, 160];
        switch (pos) {
        case 1: return [a, T, b, C];
        case 2: return [T, TR, b];
        case 3: return [TR, R, b];
        case 4: return [b, R, c, C];
        case 5: return [R, BR, c];
        case 6: return [BR, B, c];
        case 7: return [c, B, d, C];
        case 8: return [B, BL, d];
        case 9: return [BL, L, d];
        case 10: return [d, L, a, C];
        case 11: return [L, TL, a];
        default: return [TL, T, a];
        }
    }

    // Horizontal extent [min, max] that a convex polygon occupies at row y.
    function polySpanAtY(poly, y) {
        var xs = [];
        for (var i = 0; i < poly.length; i++) {
            var p1 = poly[i];
            var p2 = poly[(i + 1) % poly.length];
            var y1 = p1[1], y2 = p2[1];
            if (y1 === y2) continue;
            if ((y1 <= y && y <= y2) || (y2 <= y && y <= y1)) {
                xs.push(p1[0] + (y - y1) * (p2[0] - p1[0]) / (y2 - y1));
            }
        }
        if (xs.length < 2) return null;
        var mn = Math.min.apply(null, xs);
        var mx = Math.max.apply(null, xs);
        if (mx - mn < 1) return null;
        return { min: mn, max: mx };
    }

    // Vertical extent [min, max] that a convex polygon occupies at column x.
    function polySpanAtX(poly, x) {
        var ys = [];
        for (var i = 0; i < poly.length; i++) {
            var p1 = poly[i];
            var p2 = poly[(i + 1) % poly.length];
            var x1 = p1[0], x2 = p2[0];
            if (x1 === x2) continue;
            if ((x1 <= x && x <= x2) || (x2 <= x && x <= x1)) {
                ys.push(p1[1] + (x - x1) * (p2[1] - p1[1]) / (x2 - x1));
            }
        }
        if (ys.length < 2) return null;
        var mn = Math.min.apply(null, ys);
        var mx = Math.max.apply(null, ys);
        if (mx - mn < 1) return null;
        return { min: mn, max: mx };
    }

    // Largest font size (<= baseFont) that fits the given text within maxW.
    function fitFont(ctx, text, maxW, baseFont, minFont) {
        var min = minFont || 6;
        var fs = Math.max(min, baseFont);
        ctx.font = "bold " + fs + "px sans-serif";
        while (fs > min) {
            var w = 0;
            try { w = ctx.measureText(text).width; } catch (e) { break; }
            if (w <= maxW) break;
            fs -= 1;
            ctx.font = "bold " + fs + "px sans-serif";
        }
        return fs;
    }

    // Vertex-average centroid (inside for convex polygons).
    function polyCentroid(poly) {
        var sx = 0, sy = 0;
        for (var i = 0; i < poly.length; i++) {
            sx += poly[i][0];
            sy += poly[i][1];
        }
        return [sx / poly.length, sy / poly.length];
    }

    function clipToPolygon(ctx, poly, sx, sy) {
        ctx.beginPath();
        ctx.moveTo(sx(poly[0][0]), sy(poly[0][1]));
        for (var i = 1; i < poly.length; i++) ctx.lineTo(sx(poly[i][0]), sy(poly[i][1]));
        ctx.closePath();
        ctx.clip();
    }

    // Draw a centred block of planet glyphs at (cx, cy) inside half-width hw.
    // maxH (in device px) additionally constrains the block height; the glyphs
    // are also clipped to the enclosing cell by the caller.
    function drawPlanets(ctx, pts, cx, cy, hw, baseFont, maxH) {
        if (!pts || pts.length === 0) return;
        var gly = glyphs[langKey] || glyphs["en"];
        var n = pts.length;
        var cols = n <= 3 ? 3 : 2;
        var rowsP = Math.ceil(n / cols);
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        // Measure the widest label; shrink the font until the block fits the cell.
        var fs = baseFont;
        var maxW = 0;
        ctx.font = "bold " + fs + "px sans-serif";
        for (var i = 0; i < n; i++) {
            try { maxW = Math.max(maxW, ctx.measureText(gly[pts[i]]).width); } catch (e) { maxW = fs * 2; }
        }
        function blockFits() {
            var spacingY = fs + 3;
            var xspace = cols > 1 ? Math.min(maxW + 3, 2 * hw / (cols - 1)) : Math.min(maxW + 2, hw);
            var rowW = (cols - 1) * xspace + maxW;
            var h = rowsP * spacingY;
            return rowW <= 2 * hw && (maxH <= 0 || h <= maxH);
        }
        while (fs > 6 && !blockFits()) {
            fs -= 1;
            maxW = 0;
            ctx.font = "bold " + fs + "px sans-serif";
            for (var i = 0; i < n; i++) {
                try { maxW = Math.max(maxW, ctx.measureText(gly[pts[i]]).width); } catch (e) { maxW = fs * 2; }
            }
        }

        var spacingY = fs + 3;
        var y0 = cy - (rowsP - 1) * spacingY / 2;
        var xspace = cols > 1 ? Math.min(maxW + 3, 2 * hw / (cols - 1)) : Math.min(maxW + 2, hw);
        ctx.font = "bold " + fs + "px sans-serif";

        for (var r = 0; r < rowsP; r++) {
            var from = r * cols;
            var to = Math.min(from + cols, n);
            var count = to - from;
            var totalW = (count - 1) * xspace;
            var x0 = cx - totalW / 2;
            for (var c = from; c < to; c++) {
                var pidx = pts[c];
                var gx = x0 + (c - from) * xspace;
                var gw = 0;
                try { gw = ctx.measureText(gly[pidx]).width; } catch (e) { gw = 12; }
                ctx.fillStyle = colors && colors[pidx] ? colors[pidx] : "white";
                ctx.fillText(gly[pidx], gx - gw / 2, y0 + r * spacingY);
                if (markers && markers[pidx]) {
                    if (markers[pidx].retro) {
                        ctx.font = "bold " + (fs - 2) + "px sans-serif";
                        ctx.fillStyle = retroColor;
                        ctx.fillText("ᴿ", gx + gw / 2 + 2, y0 + r * spacingY - 1);
                    }
                    if (markers[pidx].combust) {
                        ctx.fillStyle = combustColor;
                        ctx.beginPath();
                        ctx.arc(gx + gw / 2 + 5, y0 + r * spacingY, 1.5, 0, 2 * Math.PI);
                        ctx.fill();
                    }
                }
                ctx.font = "bold " + fs + "px sans-serif";
            }
        }
    }

    function setCtxDefaults(ctx) {
        ctx.strokeStyle = lineColor;
        ctx.lineWidth = 1.4;
    }

    // ---------- North Indian (diamond) ----------

    function paintNorth(ctx) {
        var S = 320, m = 18;
        var o = [[m, m], [S - m, m], [S - m, S - m], [m, S - m]];
        var T = [S / 2, m], R = [S - m, S / 2], B = [S / 2, S - m], L = [m, S / 2];

        function sx(x) { return x / S * chart.width; }
        function sy(y) { return y / S * chart.height; }

        setCtxDefaults(ctx);

        // Outer square
        ctx.beginPath();
        ctx.moveTo(sx(o[0][0]), sy(o[0][1]));
        for (var i = 1; i < 4; i++) ctx.lineTo(sx(o[i][0]), sy(o[i][1]));
        ctx.closePath();
        ctx.stroke();

        // Diamond (L-T-R-B)
        ctx.beginPath();
        ctx.moveTo(sx(T[0]), sy(T[1]));
        ctx.lineTo(sx(R[0]), sy(R[1]));
        ctx.lineTo(sx(B[0]), sy(B[1]));
        ctx.lineTo(sx(L[0]), sy(L[1]));
        ctx.closePath();
        ctx.stroke();

        // Diagonals
        ctx.beginPath();
        ctx.moveTo(sx(o[0][0]), sy(o[0][1]));
        ctx.lineTo(sx(o[2][0]), sy(o[2][1]));
        ctx.moveTo(sx(o[1][0]), sy(o[1][1]));
        ctx.lineTo(sx(o[3][0]), sy(o[3][1]));
        ctx.stroke();

        // Per-house centroid anchors (in virtual 320 space).
        var cxTable = [0, 160, 236, 262, 250, 262, 236, 160, 84, 58, 70, 58, 84];
        var cyTable = [0, 58, 58, 118, 160, 202, 262, 262, 262, 202, 160, 118, 58];
        // House-number corners (near the outer tip of each cell).
        var nxTable = [0, 160, 238, 260, 246, 260, 238, 160, 82, 60, 74, 60, 82];
        var nyTable = [0, 30, 34, 108, 148, 186, 252, 258, 34, 148, 92, 24, 34];

        var gly = glyphs[langKey] || glyphs["en"];
        var rgly = rashiGlyphs[langKey] || rashiGlyphs["en"];
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        // Houses run ANTICLOCKWISE: house h occupies the cell where the
        // clockwise layout would draw house pos = (13 - h) % 12 + 1.
        var rf = Math.max(9, Math.floor(chart.width / 42) + 3);
        var hf = Math.max(7, Math.floor(chart.width / 44) + 2);
        var pf = Math.max(11, Math.floor(chart.width / 38) + 3);
        var pan = Math.max(50, Math.floor(chart.width / 5.5));
        for (var h = 1; h <= 12; h++) {
            var pos = ((13 - h) % 12) + 1;
            var ship = (ascRashi + h - 1) % 12;
            var cx = cxTable[pos], cy = cyTable[pos], nx = nxTable[pos], ny = nyTable[pos];
            var pts = planetListForShip(ship);
            var poly = northPoly(pos);

            // House number at the cell corner (kept outside the clip so it is legible)
            ctx.font = hf + "px sans-serif";
            ctx.fillStyle = Qt.rgba(0.9, 0.9, 0.9, 0.35);
            ctx.fillText(String(h), sx(nx), sy(ny));

            // Clip rashi name + planets to the house polygon so nothing crosses it.
            ctx.save();
            clipToPolygon(ctx, poly, sx, sy);

            // Rashi label at the house centroid top (full name, shrinks to fit the cell)
            var span = polySpanAtY(poly, cy - 8);
            var rashiMaxW = span ? (span.max - span.min) * 0.92 : pan;
            var rf2 = fitFont(ctx, rgly[ship], rashiMaxW * chart.width / S, rf, 7);
            ctx.font = rf2 + "px sans-serif";
            ctx.fillStyle = labelColor;
            ctx.fillText(rgly[ship], sx(cx), sy(cy) - 8);

            // Planets — anchored at the cell centroid so the block is always
            // inside its house, sized from the spans at that point.
            var ctr = polyCentroid(poly);
            var px = ctr[0], py = ctr[1];
            var pw = polySpanAtY(poly, py);
            var ph = polySpanAtX(poly, px);
            var hw = pw ? (pw.max - pw.min) / 2 * 0.85 : pan;
            var hh = ph ? (ph.max - ph.min) / 2 * 0.85 : pan;
            drawPlanets(ctx, pts, sx(px), sy(py),
                        Math.max(8, hw * chart.width / S), pf,
                        Math.max(8, hh * chart.height / S));

            ctx.restore();
        }

        drawLegend(ctx);
    }

    // ---------- South / East Indian (4x4 fixed-sign grid) ----------

    // Mapping sign index -> (row, col).  South has Aries at top-inner-left and
    // runs clockwise; East mirrors it (run counterclockwise).
    function signTable(south) {
        // south row/col per sign; east = (row, 3-col)
        var rows = [0, 0, 0, 1, 2, 3, 3, 3, 3, 2, 1, 0];
        var cols = [1, 2, 3, 3, 3, 3, 2, 1, 0, 0, 0, 0];
        var out = [];
        for (var s = 0; s < 12; s++) {
            out.push(south ? [rows[s], cols[s]] : [rows[s], 3 - cols[s]]);
        }
        return out;
    }

    function paintGrid(ctx, east) {
        var m = 8;
        var table = signTable(!east);
        var x0 = m, y0 = m, w = chart.width - 2 * m, h = chart.height - 2 * m;
        var cw = w / 4, ch = h / 4;

        setCtxDefaults(ctx);

        // Grid lines
        ctx.beginPath();
        for (var i = 0; i <= 4; i++) {
            ctx.moveTo(x0 + i * cw, y0);
            ctx.lineTo(x0 + i * cw, y0 + h);
            ctx.moveTo(x0, y0 + i * ch);
            ctx.lineTo(x0 + w, y0 + i * ch);
        }
        ctx.stroke();

var gly = glyphs[langKey] || glyphs["en"];
        var rgly = rashiGlyphs[langKey] || rashiGlyphs["en"];
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        var rf = Math.max(9, Math.floor(cw / 9) + 4);
        var pf = Math.max(10, Math.floor(chart.width / 38) + 2);
        for (var s = 0; s < 12; s++) {
            var rc = table[s];
            var cellX = x0 + rc[1] * cw;
            var cellY = y0 + rc[0] * ch;
            var pts = planetListForShip(s);
            var houseNo = (s - ascRashi + 12) % 12 + 1;

            // Clip rashi name + planets to the cell so nothing crosses it.
            ctx.save();
            ctx.beginPath();
            ctx.rect(cellX + 1, cellY + 1, cw - 2, ch - 2);
            ctx.clip();

            // Rashi label top of the cell (full name, shrinks to fit the cell)
            var rf2 = fitFont(ctx, rgly[s], (cw - 6), rf, 7);
            ctx.font = rf2 + "px sans-serif";
            ctx.fillStyle = labelColor;
            ctx.fillText(rgly[s], cellX + cw / 2, cellY + 10);

            // House number for this sign (from lagna) top-left
            ctx.font = "9px sans-serif";
            ctx.fillStyle = Qt.rgba(0.9, 0.9, 0.9, 0.4);
            ctx.fillText(String(houseNo), cellX + 5, cellY + 5);

            // Ascendant marker
            if (s === ascRashi) {
                ctx.font = "bold 9px sans-serif";
                ctx.fillStyle = asciiMarkerColor;
                ctx.fillText("As", cellX + cw - 12, cellY + 6);
            }

            drawPlanets(ctx, pts, cellX + cw / 2, cellY + ch / 2 + 6, cw / 2, pf, ch / 2);

            ctx.restore();
        }

        // Shade the unused inner 2x2
        ctx.fillStyle = Qt.rgba(0.4, 0.4, 0.4, 0.18);
        ctx.fillRect(x0 + cw, y0 + ch, cw * 2, ch * 2);
        drawLegend(ctx);
    }

    function drawLegend(ctx) {
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        // Vakri marker
        ctx.font = "bold 9px sans-serif";
        ctx.fillStyle = retroColor;
        ctx.fillText("ᴿ " + (langKey === "devanagari" ? "वक्री" : "Vakri"), 10, chart.height - 7);
        // Asta marker
        var vakriW = 0;
        try { vakriW = ctx.measureText("ᴿ " + (langKey === "devanagari" ? "वक्री" : "Vakri")).width; } catch (e) {}
        ctx.font = "9px sans-serif";
        ctx.fillStyle = combustColor;
        ctx.beginPath();
        ctx.arc(10 + vakriW + 12, chart.height - 7, 3, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillText(langKey === "devanagari" ? "अस्त" : "Asta", 10 + vakriW + 20, chart.height - 7);
    }
}