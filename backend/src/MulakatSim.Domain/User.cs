namespace MulakatSim.Domain;

public class User
{
    public Guid Id { get; set; } = Guid.CreateVersion7();
    public required string Email { get; set; }
    public required string DisplayName { get; set; }

    // Null for accounts that only sign in with Google.
    public string? PasswordHash { get; set; }
    public string? GoogleSubject { get; set; }

    // "tr" or "en"
    public string PreferredLanguage { get; set; } = "tr";

    public bool ConsentAudioStorage { get; set; }
    public bool ConsentCrossBorderTransfer { get; set; }

    public int DailyInterviewLimit { get; set; } = 3;

    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? DeletedAt { get; set; }

    public List<Document> Documents { get; set; } = [];
    public List<Interview> Interviews { get; set; } = [];
}
