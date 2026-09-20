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
    property var signs: []        // length 13: planet index -> rashi index (0..11)
    property var markers: []      // length 13: { retro: bool, combust: bool }
    property var colors: []       // length 13: color string per planet
    property string langKey: "en"

    property var glyphs: {
        "en": ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu", "Aruna", "Varuna", "Yama", "Maandi"],
        "iast": ["Sūrya", "Candra", "Maṅgala", "Budha", "Guru", "Śukra", "Śani", "Rāhu", "Ketu", "Aruṇa", "Varuṇa", "Yama", "Māndi"],
        "devanagari": ["सूर्य", "चन्द्र", "मङ्गल", "बुध", "गुरु", "शुक्र", "शनि", "राहु", "केतु", "अरुण", "वरुण", "यम", "मान्दि"]
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
        for (var i = 0; i < signs.length && i < 13; i++) {
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

    // Point interpolation between a and b (both [x, y] in virtual space).
    function lerpPt(a, b, t) {
        return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
    }

    // The polygon vertex farthest from the centroid — the "outer tip" of the
    // house, used to anchor the rashi number just inside the boundary.
    function tipVertex(poly, ctr) {
        var best = poly[0], bd = -1;
        for (var i = 0; i < poly.length; i++) {
            var dx = poly[i][0] - ctr[0], dy = poly[i][1] - ctr[1];
            var dd = dx * dx + dy * dy;
            if (dd > bd) { bd = dd; best = poly[i]; }
        }
        return best;
    }

    function clipToPolygon(ctx, poly, sx, sy) {
        ctx.beginPath();
        ctx.moveTo(sx(poly[0][0]), sy(poly[0][1]));
        for (var i = 1; i < poly.length; i++) ctx.lineTo(sx(poly[i][0]), sy(poly[i][1]));
        ctx.closePath();
        ctx.clip();
    }

    // Draw a single-column (vertical) centred list of planet names at (cx, cy),
    // inside half-width hw. Full Indian names are always used, one per row,
    // with a uniform font size for all planets within the house.
    function drawPlanets(ctx, pts, cx, cy, hw, baseFont, maxH, forceAbbr, hwAtY) {
        if (!pts || pts.length === 0) return;
        var full = glyphs[langKey] || glyphs["en"];
        var n = pts.length;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        function textWidth(name, fsz) {
            ctx.font = "bold " + fsz + "px sans-serif";
            try { return ctx.measureText(name).width; } catch (e) { return fsz * name.length + 4; }
        }

        function widestAt(fsz) {
            var mw = 0;
            for (var k = 0; k < n; k++) mw = Math.max(mw, textWidth(full[pts[k]], fsz));
            return mw;
        }

        var maxAvail = Math.max(10, 2 * hw * 0.90);
        var fs = Math.max(10, baseFont);
        if (maxH > 0) {
            while (fs > 9 && n * (fs + 3) > maxH) fs -= 1;
        }
        while (fs > 9 && widestAt(fs) > maxAvail) fs -= 1;

        // Ensure all rows fit within tapering polygon edges at their respective Y coordinates,
        // shrinking font size uniformly for all planets in this cell if needed.
        if (hwAtY) {
            var needsShrink = true;
            while (needsShrink && fs > 9) {
                needsShrink = false;
                var spTest = fs + 3;
                var yStart = cy - (n - 1) * spTest / 2;
                for (var j = 0; j < n; j++) {
                    var testY = yStart + j * spTest;
                    var half = hwAtY(testY);
                    if (half && half > 2) {
                        var localMax = 2 * half * 0.90;
                        if (textWidth(full[pts[j]], fs) > localMax) {
                            needsShrink = true;
                            fs -= 1;
                            break;
                        }
                    }
                }
            }
        }

        var spacingY = fs + 3;
        var y0 = cy - (n - 1) * spacingY / 2;

        for (var i = 0; i < n; i++) {
            var pidx = pts[i];
            var ty = y0 + i * spacingY;
            var gw = textWidth(full[pidx], fs);
            var col = colors && colors[pidx] ? colors[pidx] : "white";
            ctx.font = "bold " + fs + "px sans-serif";
            ctx.lineWidth = Math.max(1, Math.round(fs * 0.18));
            ctx.strokeStyle = Qt.rgba(0.03, 0.03, 0.06, 0.75);
            ctx.strokeText(full[pidx], cx, ty);
            ctx.fillStyle = col;
            ctx.fillText(full[pidx], cx, ty);
            if (markers && markers[pidx]) {
                if (markers[pidx].retro) {
                    ctx.font = "bold " + Math.max(7, fs - 2) + "px sans-serif";
                    ctx.fillStyle = retroColor;
                    ctx.strokeStyle = "transparent";
                    ctx.fillText("ᴿ", cx + gw / 2 + 2, ty - 1);
                }
                if (markers[pidx].combust) {
                    ctx.fillStyle = combustColor;
                    ctx.beginPath();
                    ctx.arc(cx + gw / 2 + 5, ty, Math.max(1.5, fs * 0.12), 0, 2 * Math.PI);
                    ctx.fill();
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

        var gly = glyphs[langKey] || glyphs["en"];
        var rgly = rashiGlyphs[langKey] || rashiGlyphs["en"];
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        var sxf = chart.width / S;
        var syf = chart.height / S;

        // Base font sizes (device px): rashi number, rashi name, planets.
        var rf = Math.max(9, Math.floor(chart.width / 44) + 3);
        var hf = Math.max(10, Math.floor(chart.width / 46) + 4);
        var pf = Math.max(13, Math.min(17, Math.floor(chart.width / 34)));

        // Houses run ANTICLOCKWISE: house h occupies the cell where the
        // clockwise layout would draw house pos = (13 - h) % 12 + 1.
        for (var h = 1; h <= 12; h++) {
            var pos = ((13 - h) % 12) + 1;
            var ship = (ascRashi + h - 1) % 12;
            var pts = planetListForShip(ship);
            var poly = northPoly(pos);
            var ctr = polyCentroid(poly);

            ctx.save();
            clipToPolygon(ctx, poly, sx, sy);

            var numPos, namePos, pxC, pcy, maxHW, maxBH;

            if (pos === 1) { // Top Rhombus [a, T, b, C]
                numPos = [160, 32]; namePos = [160, 52]; pxC = 160; pcy = 112; maxHW = 55; maxBH = 70;
            } else if (pos === 4) { // Right Rhombus [b, R, c, C]
                numPos = [288, 160]; namePos = [266, 160]; pxC = 195; pcy = 160; maxHW = 50; maxBH = 70;
            } else if (pos === 7) { // Bottom Rhombus [c, B, d, C]
                numPos = [160, 288]; namePos = [160, 268]; pxC = 160; pcy = 208; maxHW = 55; maxBH = 70;
            } else if (pos === 10) { // Left Rhombus [d, L, a, C]
                numPos = [32, 160]; namePos = [54, 160]; pxC = 125; pcy = 160; maxHW = 50; maxBH = 70;
            } else if (pos === 2) { // Top Right Inner Triangle [T, TR, b]
                numPos = [285, 28]; namePos = [231, 28]; pxC = 231; pcy = 58; maxHW = 45; maxBH = 48;
            } else if (pos === 6) { // Bottom Right Inner Triangle [BR, B, c]
                numPos = [285, 292]; namePos = [231, 292]; pxC = 231; pcy = 262; maxHW = 45; maxBH = 48;
            } else if (pos === 8) { // Bottom Left Inner Triangle [B, BL, d]
                numPos = [35, 292]; namePos = [89, 292]; pxC = 89; pcy = 262; maxHW = 45; maxBH = 48;
            } else if (pos === 12) { // Top Left Inner Triangle [TL, T, a]
                numPos = [35, 28]; namePos = [89, 28]; pxC = 89; pcy = 58; maxHW = 45; maxBH = 48;
            } else if (pos === 3) { // Top Right Outer Triangle [TR, R, b]
                numPos = [292, 34]; namePos = [288, 70]; pxC = 264; pcy = 98; maxHW = 35; maxBH = 48;
            } else if (pos === 5) { // Bottom Right Outer Triangle [R, BR, c]
                numPos = [292, 286]; namePos = [288, 250]; pxC = 264; pcy = 222; maxHW = 35; maxBH = 48;
            } else if (pos === 9) { // Bottom Left Outer Triangle [BL, L, d]
                numPos = [28, 286]; namePos = [32, 250]; pxC = 56; pcy = 222; maxHW = 35; maxBH = 48;
            } else { // pos === 11: Top Left Outer Triangle [L, TL, a]
                numPos = [28, 34]; namePos = [32, 70]; pxC = 56; pcy = 98; maxHW = 35; maxBH = 48;
            }

            // Rashi number
            var numTxt = String(ship + 1);
            var nf = fitFont(ctx, numTxt, 24 * sxf, hf, 9);
            ctx.font = "bold " + nf + "px sans-serif";
            ctx.lineWidth = Math.max(1.5, nf * 0.16);
            ctx.strokeStyle = Qt.rgba(0.04, 0.04, 0.08, 0.85);
            ctx.strokeText(numTxt, sx(numPos[0]), sy(numPos[1]));
            ctx.fillStyle = Qt.rgba(1, 1, 1, 0.96);
            ctx.fillText(numTxt, sx(numPos[0]), sy(numPos[1]));

            // Rashi name
            var rfn = fitFont(ctx, rgly[ship], Math.max(10, maxHW * 1.8 * sxf), rf, 8);
            ctx.font = "bold " + rfn + "px sans-serif";
            ctx.fillStyle = labelColor;
            ctx.fillText(rgly[ship], sx(namePos[0]), sy(namePos[1]));

            // Planet block
            drawPlanets(ctx, pts, sx(pxC), sy(pcy),
                        Math.max(10, maxHW * sxf), pf,
                        Math.max(12, maxBH * syf), false,
                        null);

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

        var rf = Math.max(9, Math.floor(cw / 9) + 3);
        var nf = Math.max(11, Math.round(cw / 9) + 2);
        var pf = Math.max(11, Math.min(14, Math.floor(chart.width / 40) + 2));
        for (var s = 0; s < 12; s++) {
            var rc = table[s];
            var cellX = x0 + rc[1] * cw;
            var cellY = y0 + rc[0] * ch;
            var pts = planetListForShip(s);

            ctx.save();
            ctx.beginPath();
            ctx.rect(cellX + 1, cellY + 1, cw - 2, ch - 2);
            ctx.clip();

            // Rashi number, top-left, sized to the cell.
            var numTxt = String(s + 1);
            var nf2 = fitFont(ctx, numTxt, cw * 0.34, nf, 9);
            ctx.font = "bold " + nf2 + "px sans-serif";
            ctx.lineWidth = Math.max(1.5, nf2 * 0.16);
            ctx.strokeStyle = Qt.rgba(0.04, 0.04, 0.08, 0.85);
            ctx.strokeText(numTxt, cellX + 7, cellY + 6);
            ctx.fillStyle = Qt.rgba(1, 1, 1, 0.95);
            ctx.fillText(numTxt, cellX + 7, cellY + 6);

            // Rashi label top of the cell (full name)
            var rf2 = fitFont(ctx, rgly[s], (cw - 6), rf, 7);
            ctx.font = "bold " + rf2 + "px sans-serif";
            ctx.fillStyle = labelColor;
            ctx.fillText(rgly[s], cellX + cw / 2, cellY + 10);

            // Ascendant marker
            if (s === ascRashi) {
                ctx.font = "bold " + Math.max(10, nf2) + "px sans-serif";
                ctx.fillStyle = asciiMarkerColor;
                ctx.fillText(langKey === "devanagari" ? "लग्न" : "Lagna", cellX + cw - 24, cellY + 6);
            }

            drawPlanets(ctx, pts, cellX + cw / 2, cellY + ch / 2 + 8, cw / 2, pf, ch / 2 - 12, false);

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