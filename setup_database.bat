@echo off
echo ===================================================
echo Configuracao do Banco de Dados para RetroTranslatorPy
echo ===================================================
echo.

REM Verifica se o MariaDB está instalado
mysql --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: MariaDB nao encontrado!
    echo Por favor, instale o MariaDB antes de continuar.
    echo Visite: https://mariadb.org/download/
    echo.
    pause
    exit /b 1
)

echo MariaDB encontrado. Continuando com a configuracao...
echo.

REM Solicita a senha do root
set /p ROOT_PASSWORD=: 

echo.
echo Criando banco de dados e usuario...

REM Executa o script SQL
mysql -u root -p%ROOT_PASSWORD% < setup_database.sql

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: Falha ao executar o script SQL.
    echo Verifique se a senha do root esta correta e tente novamente.
    echo.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo Configuracao concluida com sucesso!
echo.
echo Banco de dados: retroarch_translations
echo Usuario: root
echo Senha: 
echo ===================================================
echo.
echo O RetroTranslatorPy agora pode usar o cache de banco de dados.
echo.

pause