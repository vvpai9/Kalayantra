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
        "en": ["Su", "Ch", "Ma", "Bu", "Gu", "Sh", "Sa", "Ra", "Ke"],
        "iast": ["Sū", "Ca", "Ma", "Bu", "Gu", "Śu", "Śa", "Rā", "Ke"],
        "devanagari": ["सू", "चं", "मं", "बु", "गु", "शु", "श", "रा", "के"]
    }
    property var rashiGlyphs: {
        "en": ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"],
        "iast": ["Meṣ", "Vṛb", "Mith", "Kark", "Siṃ", "Kan", "Tul", "Vṛś", "Dhan", "Mak", "Kumb", "Mīn"],
        "devanagari": ["मेष", "वृष", "मिथ", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"]
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

    // Draw a centred block of planet glyphs at (cx, cy) inside half-width hw.
    function drawPlanets(ctx, pts, cx, cy, hw, baseFont) {
        if (!pts || pts.length === 0) return;
        var gly = glyphs[langKey] || glyphs["en"];
        var n = pts.length;
        var nChar = n >= 6;
        var fs = nChar ? baseFont - 2 : baseFont;
        var cols = n <= 3 ? 3 : 2;
        var rowsP = Math.ceil(n / cols);
        var spacingY = fs + 2;
        var y0 = cy - (rowsP - 1) * spacingY / 2;
        var xspace = 12;
        for (var r = 0; r < rowsP; r++) {
            var from = r * cols;
            var to = Math.min(from + cols, n);
            var count = to - from;
            var totalW = (count - 1) * xspace;
            var x0 = cx - totalW / 2;
            for (var c = from; c < to; c++) {
                var i = pts[c];
                var gx = x0 + (c - from) * xspace;
                // measure the glyph width so the retro/combust marks fit
                ctx.font = "bold " + (fs - 2) + "px sans-serif";
                var gw = 0;
                try { gw = ctx.measureText(gly[i]).width; } catch (e) { gw = 10; }
                ctx.font = "bold " + fs + "px sans-serif";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = colors && colors[i] ? colors[i] : "white";
                ctx.fillText(gly[i], gx - gw / 2, y0 + r * spacingY);
                if (markers && markers[i]) {
                    if (markers[i].retro) {
                        ctx.font = "bold " + (fs - 3) + "px sans-serif";
                        ctx.fillStyle = retroColor;
                        ctx.fillText("ᴿ", gx + gw / 2 + 3, y0 + r * spacingY - 1);
                    }
                    if (markers[i].combust) {
                        ctx.fillStyle = combustColor;
                        ctx.beginPath();
                        ctx.arc(gx + gw / 2 + 6, y0 + r * spacingY, 1.5, 0, 2 * Math.PI);
                        ctx.fill();
                    }
                }
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

        for (var h = 1; h <= 12; h++) {
            var ship = (ascRashi + h - 1) % 12;
            var cx = cxTable[h], cy = cyTable[h], nx = nxTable[h], ny = nyTable[h];
            var pts = planetListForShip(ship);

            // Rashi label at the house centroid top
            ctx.font = "10px sans-serif";
            ctx.fillStyle = labelColor;
            ctx.fillText(rgly[ship], sx(cx), sy(cy) - 8);

            // House number at the cell corner
            ctx.font = "9px sans-serif";
            ctx.fillStyle = Qt.rgba(0.9, 0.9, 0.9, 0.35);
            ctx.fillText(String(h), sx(nx), sy(ny));

            drawPlanets(ctx, pts, sx(cx - 14), sy(cy + 8), 60, 11);
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

        for (var s = 0; s < 12; s++) {
            var rc = table[s];
            var cellX = x0 + rc[1] * cw;
            var cellY = y0 + rc[0] * ch;
            var pts = planetListForShip(s);

            // Rashi label top of the cell
            ctx.font = "11px sans-serif";
            ctx.fillStyle = labelColor;
            ctx.fillText(rgly[s], cellX + cw / 2, cellY + 10);

            // House number for this sign (from lagna) top-left
            var houseNo = ((s - ascRashi + 12) % 12) + 1;
            ctx.font = "9px sans-serif";
            ctx.fillStyle = Qt.rgba(0.9, 0.9, 0.9, 0.4);
            ctx.fillText(String(houseNo), cellX + 5, cellY + 5);

            // Ascendant marker
            if (s === ascRashi) {
                ctx.font = "bold 9px sans-serif";
                ctx.fillStyle = asciiMarkerColor;
                ctx.fillText("As", cellX + cw - 12, cellY + 6);
            }

            drawPlanets(ctx, pts, cellX + cw / 2, cellY + ch / 2 + 6, cw / 2, 10);
        }

        // Shade the unused inner 2x2
        ctx.fillStyle = Qt.rgba(0.4, 0.4, 0.4, 0.18);
        ctx.fillRect(x0 + cw, y0 + ch, cw * 2, ch * 2);
        drawLegend(ctx);
    }

    function drawLegend(ctx) {
        ctx.font = "9px sans-serif";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.fillStyle = labelColor;
        ctx.fillText("ᴿ Vakri   • Asta", 10, chart.height - 6);
    }
}