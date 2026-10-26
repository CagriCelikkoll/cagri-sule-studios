# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Restore first so the layer is cached until project files change.
COPY src/MulakatSim.Domain/MulakatSim.Domain.csproj src/MulakatSim.Domain/
COPY src/MulakatSim.Infrastructure/MulakatSim.Infrastructure.csproj src/MulakatSim.Infrastructure/
COPY src/MulakatSim.Api/MulakatSim.Api.csproj src/MulakatSim.Api/
RUN dotnet restore src/MulakatSim.Api/MulakatSim.Api.csproj

COPY src/ src/
RUN dotnet publish src/MulakatSim.Api/MulakatSim.Api.csproj -c Release -o /app/publish --no-restore /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
ENV ASPNETCORE_HTTP_PORTS=8080
EXPOSE 8080
COPY --from=build /app/publish .
USER $APP_UID
ENTRYPOINT ["dotnet", "MulakatSim.Api.dll"]
