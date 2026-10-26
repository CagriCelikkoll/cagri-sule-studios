namespace MulakatSim.Domain;

public class UsageLedgerEntry
{
    public Guid Id { get; set; } = Guid.CreateVersion7();
    public Guid UserId { get; set; }
    public Guid? InterviewId { get; set; }

    public UsageKind Kind { get; set; }

    // LLM model name or speech provider/voice.
    public required string Model { get; set; }

    public int InputTokens { get; set; }
    public int OutputTokens { get; set; }
    public int CacheReadTokens { get; set; }
    public long AudioMs { get; set; }

    public DateTimeOffset CreatedAt { get; set; }
}
