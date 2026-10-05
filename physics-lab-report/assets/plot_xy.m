function results = plot_xy(csvPath, outputDir, xName, yName, xLabel, yLabel, fitLine)
% Adapt to the actual physical model; columns and units are explicit inputs.
arguments
    csvPath
    outputDir
    xName
    yName
    xLabel
    yLabel
    fitLine (1,1) logical = false
end
data = readtable(csvPath, 'VariableNamingRule', 'preserve');
x = data.(xName); y = data.(yName);
assert(isnumeric(x) && isnumeric(y) && numel(x) == numel(y) && numel(x) >= 2, 'Need paired numeric data');
assert(all(isfinite(x)) && all(isfinite(y)), 'Resolve missing/non-finite measurements against the source');
results = struct('n', numel(x), 'fit', fitLine);
if fitLine
    assert(numel(x) >= 3 && max(x) > min(x), 'Fit requires >=3 pairs and variable x');
    xMean = mean(x); yMean = mean(y);
    centeredX = x - xMean; centeredY = y - yMean;
    scale = max(abs(centeredX)); design = [centeredX/scale, ones(size(x))];
    assert(rank(design) == 2, 'Numerically singular fit');
    coefficients = design \ centeredY;
    slope = coefficients(1)/scale;
    yReference = yMean + coefficients(2);
    residuals = centeredY - (slope*centeredX + coefficients(2));
    sse = sum(residuals.^2); sst = sum((y - mean(y)).^2);
    results.slope = slope; results.intercept = yReference - slope*xMean;
    results.x_reference = xMean; results.y_at_reference = yReference;
    if sst == 0, results.r_squared = NaN; else, results.r_squared = 1 - sse/sst; end
    results.residual_std = sqrt(sse/(numel(x)-2));
end
if ~isfolder(outputDir), mkdir(outputDir); end
fig = figure('Visible', 'off'); cleanup = onCleanup(@() close(fig));
scatter(x, y, 28, 'filled', 'DisplayName', '测量值'); hold on;
if fitLine
    xGrid = linspace(min(x), max(x), 200);
    plot(xGrid, results.slope * (xGrid-results.x_reference) + results.y_at_reference, 'DisplayName', '线性拟合');
end
set(gca, 'FontName', 'Times New Roman');
xlabel(xLabel, 'Interpreter', 'none', 'FontName', '宋体');
ylabel(yLabel, 'Interpreter', 'none', 'FontName', '宋体');
legend('Location', 'best', 'FontName', '宋体'); grid on;
exportgraphics(fig, fullfile(outputDir, 'data_plot.png'), 'Resolution', 300);
fid = fopen(fullfile(outputDir, 'results.json'), 'w');
assert(fid >= 0, 'Cannot open results file'); fileCleanup = onCleanup(@() fclose(fid));
fwrite(fid, jsonencode(results), 'char');
end
