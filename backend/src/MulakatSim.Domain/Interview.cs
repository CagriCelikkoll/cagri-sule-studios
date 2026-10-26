using System.Text.Json;

namespace MulakatSim.Domain;

public class Interview
{
    private static readonly Dictionary<InterviewStatus, InterviewStatus[]> AllowedTransitions = new()
    {
        [InterviewStatus.Created] = [InterviewStatus.Active, InterviewStatus.Failed, InterviewStatus.Deleted],
        [InterviewStatus.Active] = [InterviewStatus.Paused, InterviewStatus.Completed, InterviewStatus.Failed, InterviewStatus.Deleted],
        [InterviewStatus.Paused] = [InterviewStatus.Active, InterviewStatus.Completed, InterviewStatus.Failed, InterviewStatus.Deleted],
        [InterviewStatus.Completed] = [InterviewStatus.Reported, InterviewStatus.Failed, InterviewStatus.Deleted],
        [InterviewStatus.Reported] = [InterviewStatus.Deleted],
        [InterviewStatus.Failed] = [InterviewStatus.Deleted],
        [InterviewStatus.Deleted] = [],
    };

    public Guid Id { get; set; } = Guid.CreateVersion7();
    public Guid UserId { get; set; }
    public User? User { get; set; }

    public required string PersonaId { get; set; }
    public int PersonaVersion { get; set; }

    // "tr" or "en"
    public required string Language { get; set; }
    public InterviewMode Mode { get; set; }
    public int DurationMin { get; set; }

    public required string Role { get; set; }
    public CandidateLevel Level { get; set; }
    public List<string> Technologies { get; set; } = [];

    public Guid? CvDocumentId { get; set; }
    public Guid? JobPostingDocumentId { get; set; }

    public InterviewStatus Status { get; private set; } = InterviewStatus.Created;

    // Plan returned by the AI service (contracts/schemas/plan.schema.json), stored as jsonb.
    public JsonDocument? Plan { get; set; }

    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? StartedAt { get; private set; }
    public DateTimeOffset? CompletedAt { get; private set; }

    public List<Turn> Turns { get; set; } = [];
    public Report? Report { get; set; }

    public bool CanTransitionTo(InterviewStatus next) => AllowedTransitions[Status].Contains(next);

    public void TransitionTo(InterviewStatus next, DateTimeOffset now)
    {
        if (!CanTransitionTo(next))
        {
            throw new InvalidOperationException($"Invalid interview status transition: {Status} -> {next}.");
        }

        if (next == InterviewStatus.Active)
        {
            StartedAt ??= now;
        }
        else if (next == InterviewStatus.Completed)
        {
            CompletedAt = now;
        }

        Status = next;
    }
}
