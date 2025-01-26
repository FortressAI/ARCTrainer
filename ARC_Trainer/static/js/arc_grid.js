class Grid {
    constructor(height, width, values) {
        this.height = height;
        this.width = width;
        this.grid = new Array(height);
        for (let i = 0; i < height; i++) {
            this.grid[i] = new Array(width);
            for (let j = 0; j < width; j++) {
                this.grid[i][j] = values?.[i]?.[j] ?? 0;
            }
        }
    }
}

function floodfillFromLocation(grid, i, j, symbol) {
    i = parseInt(i);
    j = parseInt(j);
    symbol = parseInt(symbol);
    let target = grid[i][j];
    if (target === symbol) return;

    function flow(i, j, symbol, target) {
        if (i >= 0 && i < grid.length && j >= 0 && j < grid[i].length) {
            if (grid[i][j] === target) {
                grid[i][j] = symbol;
                flow(i - 1, j, symbol, target);
                flow(i + 1, j, symbol, target);
                flow(i, j - 1, symbol, target);
                flow(i, j + 1, symbol, target);
            }
        }
    }
    flow(i, j, symbol, target);
}

function parseSizeTuple(size) {
    let dimensions = size.split('x').map(Number);
    if (dimensions.length !== 2 || dimensions.some(n => n < 1 || n > 30)) {
        alert('Grid size should have the format "3x3", "5x7", etc., with values between 1 and 30.');
        return;
    }
    return dimensions;
}

function convertSerializedGridToGridObject(values) {
    return new Grid(values.length, values[0].length, values);
}

function fillJqGridWithData(jqGrid, dataGrid) {
    jqGrid.empty();
    for (let i = 0; i < dataGrid.height; i++) {
        let row = $('<div class="row"></div>');
        for (let j = 0; j < dataGrid.width; j++) {
            let cell = $('<div class="cell"></div>').attr({ x: i, y: j }).addClass(`symbol_${dataGrid.grid[i][j]}`);
            row.append(cell);
        }
        jqGrid.append(row);
    }
}

function setCellSymbol(cell, symbol) {
    cell.attr('symbol', symbol).removeClass().addClass(`cell symbol_${symbol}`).text($('#show_symbol_numbers').is(':checked') ? symbol : '');
}

function changeSymbolVisibility() {
    $('.cell').each((_, cell) => $(cell).text($('#show_symbol_numbers').is(':checked') ? $(cell).attr('symbol') : ''));
}

function infoMsg(msg) {
    $('#info_display').stop(true, true).hide().text(msg).fadeIn().fadeOut(5000);
}

function errorMsg(msg) {
    $('#error_display').stop(true, true).hide().text(msg).fadeIn().fadeOut(5000);
}
