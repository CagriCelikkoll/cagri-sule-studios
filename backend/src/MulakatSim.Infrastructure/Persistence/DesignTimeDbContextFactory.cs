using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

namespace MulakatSim.Infrastructure.Persistence;

// Used only by `dotnet ef` tooling; no database connection is opened when adding migrations.
public class DesignTimeDbContextFactory : IDesignTimeDbContextFactory<AppDbContext>
{
    public AppDbContext CreateDbContext(string[] args)
    {
        var options = new DbContextOptionsBuilder<AppDbContext>();
        DependencyInjection.ConfigureDbContext(options, "Host=localhost;Database=mulakatsim;Username=mulakatsim;Password=design-time");
        return new AppDbContext(options.Options);
    }
}
