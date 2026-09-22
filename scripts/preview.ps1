$ErrorActionPreference = "Stop"
$bundlerVersion = "2.5.6"

if (Get-Command ruby -ErrorAction SilentlyContinue) {
  gem install bundler --version $bundlerVersion --no-document
  bundle "_$($bundlerVersion)_" config set path vendor/bundle
  bundle "_$($bundlerVersion)_" install
  py scripts\validate_content.py
  bundle "_$($bundlerVersion)_" exec jekyll serve --livereload
  exit $LASTEXITCODE
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
  docker run --rm -it -p 4000:4000 -v "${PWD}:/site" -w /site ruby:3.3.12 `
    bash -lc "gem install bundler -v 2.5.6 --no-document && bundle _2.5.6_ install && bundle _2.5.6_ exec jekyll serve --host 0.0.0.0 --livereload"
  exit $LASTEXITCODE
}

Write-Error "Local preview requires Ruby + Bundler or Docker Desktop. See BUILD_SPEC.md."
