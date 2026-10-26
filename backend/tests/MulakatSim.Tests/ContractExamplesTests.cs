using System.Text.Json;

namespace MulakatSim.Tests;

public class ContractExamplesTests
{
    private static readonly string ExamplesDir = Path.Combine(FindRepoRoot(), "contracts", "examples");

    [Theory]
    [InlineData("hub-envelope")]
    [InlineData("persona-list")]
    [InlineData("plan-request")]
    [InlineData("plan")]
    [InlineData("report-request")]
    [InlineData("report")]
    [InlineData("turn-final")]
    [InlineData("turn-request")]
    [InlineData("turn-request-opening")]
    public void Expected_example_exists(string name)
    {
        Assert.True(File.Exists(Path.Combine(ExamplesDir, $"{name}.json")), $"Missing contracts/examples/{name}.json");
    }

    [Fact]
    public void All_examples_are_valid_json()
    {
        var files = Directory.GetFiles(ExamplesDir, "*.json");
        Assert.NotEmpty(files);

        foreach (var file in files)
        {
            var ex = Record.Exception(() => JsonDocument.Parse(File.ReadAllText(file)).Dispose());
            Assert.True(ex is null, $"{Path.GetFileName(file)} is not valid JSON: {ex?.Message}");
        }
    }

    private static string FindRepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "contracts", "examples")))
        {
            dir = dir.Parent;
        }

        return dir?.FullName ?? throw new DirectoryNotFoundException("Could not locate repository root containing contracts/examples.");
    }
}
