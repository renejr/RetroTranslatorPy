@echo off
echo Atualizando README.md com informacoes do cache de banco de dados...

REM Verifica se o arquivo README_UPDATED.md existe
if not exist README_UPDATED.md (
    echo ERRO: Arquivo README_UPDATED.md nao encontrado!
    pause
    exit /b 1
)

REM Faz backup do README.md original
if exist README.md (
    echo Criando backup do README.md original...
    copy README.md README.md.bak
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao criar backup do README.md!
        pause
        exit /b 1
    )
    echo Backup criado: README.md.bak
)

REM Substitui o README.md pelo README_UPDATED.md
copy README_UPDATED.md README.md
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao atualizar README.md!
    pause
    exit /b 1
)

echo README.md atualizado com sucesso!
echo.
echo NOTA: Um backup do README.md original foi criado como README.md.bak
echo.

pause