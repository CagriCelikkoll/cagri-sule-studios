namespace MulakatSim.Domain;

// Denormalized from Report.Content so progress queries do not have to read jsonb.
public class CompetencyScore
{
    public Guid Id { get; set; } = Guid.CreateVersion7();
    public Guid ReportId { get; set; }
    public Report? Report { get; set; }
    public Guid UserId { get; set; }

    // e.g. "communication", see ai-service/rubrics/competencies.yaml
    public required string CompetencyId { get; set; }
    public int Score { get; set; }

    public DateTimeOffset CreatedAt { get; set; }
}
