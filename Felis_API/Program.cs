//var builder = WebApplication.CreateBuilder(args);
//
//builder.Services.AddControllers();
//
//builder.Services.AddCors(options =>
//{
//    options.AddPolicy("AllowReact", policy =>
//    {
//        policy
//            .WithOrigins("http://localhost:3000", "http://localhost:5173")
//            .AllowAnyHeader()
//            .AllowAnyMethod();
//    });
//});
//
//var app = builder.Build();
//
//app.UseCors("AllowReact");
//
//app.MapControllers();
//
//app.Run();

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddHttpClient<ThingsTheUserHasController>();

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReact", policy =>
    {
        policy
            .WithOrigins(
                "http://localhost:3000",
                "http://localhost:5173",
                "https://localhost:3000",
                "https://localhost:5173"
            )
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

var app = builder.Build();

app.UseCors("AllowReact");

app.MapControllers();

app.Run();