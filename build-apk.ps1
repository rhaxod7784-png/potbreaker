$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Tools = Join-Path $ProjectRoot ".tools"
New-Item -ItemType Directory -Force -Path $Tools | Out-Null

Write-Host "[POT BREAKER] Android v0.16.0 build" -ForegroundColor Cyan

# Java: prefer JAVA_HOME, then Android Studio bundled JBR, then PATH.
if (-not $env:JAVA_HOME) {
    $StudioJbr = "C:\Program Files\Android\Android Studio\jbr"
    if (Test-Path (Join-Path $StudioJbr "bin\java.exe")) {
        $env:JAVA_HOME = $StudioJbr
    }
}

if ($env:JAVA_HOME) {
    $env:Path = "$($env:JAVA_HOME)\bin;$($env:Path)"
}

if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    throw "Java not found. Install Android Studio or JDK 17+ and run this script again."
}

# Android SDK: use existing installation when possible.
$Sdk = $env:ANDROID_SDK_ROOT
if (-not $Sdk) { $Sdk = $env:ANDROID_HOME }
if (-not $Sdk) {
    $DefaultSdk = Join-Path $env:LOCALAPPDATA "Android\Sdk"
    if (Test-Path $DefaultSdk) { $Sdk = $DefaultSdk }
}

if (-not $Sdk) {
    $Sdk = Join-Path $Tools "android-sdk"
    $CmdlineZip = Join-Path $Tools "commandlinetools-win.zip"
    $CmdlineUrl = "https://dl.google.com/android/repository/commandlinetools-win-15859902_latest.zip"

    if (-not (Test-Path $CmdlineZip)) {
        Write-Host "Downloading Android command-line tools..."
        Invoke-WebRequest -Uri $CmdlineUrl -OutFile $CmdlineZip
    }

    $CmdRoot = Join-Path $Sdk "cmdline-tools"
    $Latest = Join-Path $CmdRoot "latest"
    if (-not (Test-Path (Join-Path $Latest "bin\sdkmanager.bat"))) {
        $TempExtract = Join-Path $Tools "cmdline-extract"
        Remove-Item -Recurse -Force $TempExtract -ErrorAction SilentlyContinue
        Expand-Archive -Path $CmdlineZip -DestinationPath $TempExtract -Force
        New-Item -ItemType Directory -Force -Path $CmdRoot | Out-Null
        Remove-Item -Recurse -Force $Latest -ErrorAction SilentlyContinue
        Move-Item (Join-Path $TempExtract "cmdline-tools") $Latest
    }

    $SdkManager = Join-Path $Latest "bin\sdkmanager.bat"
    Write-Host "Installing Android SDK 35 components..."
    cmd /c "echo y|`"$SdkManager`" --sdk_root=`"$Sdk`" --licenses" | Out-Null
    & $SdkManager --sdk_root=$Sdk "platform-tools" "platforms;android-35" "build-tools;35.0.0"
}

$env:ANDROID_HOME = $Sdk
$env:ANDROID_SDK_ROOT = $Sdk
$SdkForGradle = $Sdk.Replace('\','/')
"sdk.dir=$SdkForGradle" | Set-Content -Encoding ASCII (Join-Path $ProjectRoot "local.properties")

# Gradle 8.10.2 for AGP 8.8.x.
$GradleVersion = "8.10.2"
$GradleDir = Join-Path $Tools "gradle-$GradleVersion"
$GradleBat = Join-Path $GradleDir "bin\gradle.bat"
if (-not (Test-Path $GradleBat)) {
    $GradleZip = Join-Path $Tools "gradle-$GradleVersion-bin.zip"
    if (-not (Test-Path $GradleZip)) {
        Write-Host "Downloading Gradle $GradleVersion..."
        Invoke-WebRequest -Uri "https://services.gradle.org/distributions/gradle-$GradleVersion-bin.zip" -OutFile $GradleZip
    }
    Expand-Archive -Path $GradleZip -DestinationPath $Tools -Force
}

Push-Location $ProjectRoot
try {
    & $GradleBat --no-daemon assembleDebug
    if ($LASTEXITCODE -ne 0) { throw "Gradle build failed." }
} finally {
    Pop-Location
}

$BuiltApk = Join-Path $ProjectRoot "app\build\outputs\apk\debug\app-debug.apk"
$OutApk = Join-Path $ProjectRoot "POT_BREAKER-v0.16.0-android-debug.apk"
Copy-Item $BuiltApk $OutApk -Force
Write-Host "APK created: $OutApk" -ForegroundColor Green
