namespace MulakatSim.Domain;

public class Document
{
    public Guid Id { get; set; } = Guid.CreateVersion7();
    public Guid UserId { get; set; }
    public User? User { get; set; }

    public DocumentKind Kind { get; set; }

    // Null when the document was submitted as plain text.
    public string? FileName { get; set; }
    public string? StorageKey { get; set; }

    // Text after PII masking; the unmasked text is never persisted.
    public required string MaskedText { get; set; }
    public int CharCount { get; set; }
    public List<string> MaskedFields { get; set; } = [];

    public DateTimeOffset CreatedAt { get; set; }
}
