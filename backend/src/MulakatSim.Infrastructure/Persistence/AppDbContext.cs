using MulakatSim.Domain;
using Microsoft.EntityFrameworkCore;

namespace MulakatSim.Infrastructure.Persistence;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();
    public DbSet<Document> Documents => Set<Document>();
    public DbSet<Interview> Interviews => Set<Interview>();
    public DbSet<Turn> Turns => Set<Turn>();
    public DbSet<Report> Reports => Set<Report>();
    public DbSet<CompetencyScore> CompetencyScores => Set<CompetencyScore>();
    public DbSet<UsageLedgerEntry> UsageLedger => Set<UsageLedgerEntry>();

    protected override void ConfigureConventions(ModelConfigurationBuilder configurationBuilder)
    {
        // Enums are stored as readable strings.
        configurationBuilder.Properties<InterviewStatus>().HaveConversion<string>().HaveMaxLength(20);
        configurationBuilder.Properties<InterviewMode>().HaveConversion<string>().HaveMaxLength(20);
        configurationBuilder.Properties<CandidateLevel>().HaveConversion<string>().HaveMaxLength(20);
        configurationBuilder.Properties<Speaker>().HaveConversion<string>().HaveMaxLength(20);
        configurationBuilder.Properties<DocumentKind>().HaveConversion<string>().HaveMaxLength(20);
        configurationBuilder.Properties<UsageKind>().HaveConversion<string>().HaveMaxLength(20);
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(e =>
        {
            e.Property(x => x.Email).HasMaxLength(320);
            e.Property(x => x.DisplayName).HasMaxLength(100);
            e.Property(x => x.PreferredLanguage).HasMaxLength(2);
            e.HasIndex(x => x.Email).IsUnique();
            e.HasIndex(x => x.GoogleSubject).IsUnique().HasFilter("google_subject IS NOT NULL");
        });

        modelBuilder.Entity<Document>(e =>
        {
            e.Property(x => x.FileName).HasMaxLength(255);
            e.HasOne(x => x.User).WithMany(x => x.Documents).HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => new { x.UserId, x.CreatedAt });
        });

        modelBuilder.Entity<Interview>(e =>
        {
            e.Property(x => x.PersonaId).HasMaxLength(100);
            e.Property(x => x.Language).HasMaxLength(2);
            e.Property(x => x.Role).HasMaxLength(100);
            e.Property(x => x.Plan).HasColumnType("jsonb");
            e.HasOne(x => x.User).WithMany(x => x.Interviews).HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
            e.HasOne<Document>().WithMany().HasForeignKey(x => x.CvDocumentId).OnDelete(DeleteBehavior.SetNull);
            e.HasOne<Document>().WithMany().HasForeignKey(x => x.JobPostingDocumentId).OnDelete(DeleteBehavior.SetNull);
            e.HasIndex(x => new { x.UserId, x.CreatedAt });
        });

        modelBuilder.Entity<Turn>(e =>
        {
            e.Property(x => x.QuestionId).HasMaxLength(20);
            e.Property(x => x.Metrics).HasColumnType("jsonb");
            e.HasOne(x => x.Interview).WithMany(x => x.Turns).HasForeignKey(x => x.InterviewId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => new { x.InterviewId, x.Index }).IsUnique();
        });

        modelBuilder.Entity<Report>(e =>
        {
            e.Property(x => x.Content).HasColumnType("jsonb");
            e.HasOne(x => x.Interview).WithOne(x => x.Report).HasForeignKey<Report>(x => x.InterviewId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => x.InterviewId).IsUnique();
        });

        modelBuilder.Entity<CompetencyScore>(e =>
        {
            e.Property(x => x.CompetencyId).HasMaxLength(50);
            e.HasOne(x => x.Report).WithMany(x => x.CompetencyScores).HasForeignKey(x => x.ReportId).OnDelete(DeleteBehavior.Cascade);
            e.HasIndex(x => new { x.UserId, x.CompetencyId, x.CreatedAt });
        });

        modelBuilder.Entity<UsageLedgerEntry>(e =>
        {
            e.ToTable("usage_ledger");
            e.Property(x => x.Model).HasMaxLength(100);
            e.HasOne<User>().WithMany().HasForeignKey(x => x.UserId).OnDelete(DeleteBehavior.Cascade);
            e.HasOne<Interview>().WithMany().HasForeignKey(x => x.InterviewId).OnDelete(DeleteBehavior.SetNull);
            e.HasIndex(x => new { x.UserId, x.CreatedAt });
        });
    }
}
