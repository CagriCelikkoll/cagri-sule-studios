using System.Text.Json;

namespace MulakatSim.Domain;

public class Report
{
    public Guid Id { get; set; } = Guid.CreateVersion7();
    public Guid InterviewId { get; set; }
    public Interview? Interview { get; set; }

    public int RubricVersion { get; set; }
    public int OverallScore { get; set; }

    // Report returned by the AI service (contracts/schemas/report.schema.json), stored as jsonb.
    public required JsonDocument Content { get; set; }

    public DateTimeOffset CreatedAt { get; set; }

    public List<CompetencyScore> CompetencyScores { get; set; } = [];
}
