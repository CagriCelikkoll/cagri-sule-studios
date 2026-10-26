using System.Text.Json;

namespace MulakatSim.Domain;

public class Turn
{
    public Guid Id { get; set; } = Guid.CreateVersion7();
    public Guid InterviewId { get; set; }
    public Interview? Interview { get; set; }

    // Position in the interview, starting at 0; unique per interview.
    public int Index { get; set; }
    public Speaker Speaker { get; set; }
    public required string Text { get; set; }
    public string? QuestionId { get; set; }
    public int? InterruptedAtChar { get; set; }

    // Offsets from interview start, in milliseconds.
    public long? StartMs { get; set; }
    public long? EndMs { get; set; }

    public string? AudioStorageKey { get; set; }

    // Candidate turn metrics (turn_metrics in contracts/schemas/common.schema.json), stored as jsonb.
    public JsonDocument? Metrics { get; set; }

    public DateTimeOffset CreatedAt { get; set; }
}
