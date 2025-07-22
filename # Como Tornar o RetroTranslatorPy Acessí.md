# Como Tornar o RetroTranslatorPy Acessível pela Internet

Para disponibilizar seu serviço RetroTranslatorPy na internet usando seu domínio no-ip (mdxhq.servegame.com), precisamos realizar algumas configurações. Vou explicar o processo passo a passo:

## 1. Configuração do Servidor

O seu servidor já está configurado para aceitar conexões externas, pois no arquivo `main.py` você está usando:

```python
uvicorn.run(app, host="0.0.0.0", port=4404)
```

O parâmetro `host="0.0.0.0"` significa que o servidor aceita conexões de qualquer endereço IP, não apenas do localhost. Isso é essencial para acesso externo.

## 2. Configuração do Roteador

Para que seu serviço seja acessível pela internet, você precisa configurar o redirecionamento de porta no seu roteador:

1. **Acesse a interface de administração do seu roteador** (geralmente http://192.168.0.1 ou http://192.168.1.1)
2. **Procure a seção de "Port Forwarding" ou "Redirecionamento de Portas"**
3. **Adicione uma nova regra com as seguintes configurações**:
   - **Porta externa**: 4404 (a mesma porta que seu serviço usa)
   - **Porta interna**: 4404
   - **Endereço IP interno**: O endereço IP local do seu computador (verifique usando o comando `ipconfig` no Windows)
   - **Protocolo**: TCP (ou TCP/UDP)
   - **Nome da regra**: RetroTranslatorPy (ou qualquer nome descritivo)

## 3. Configuração do Firewall do Windows

1. **Abra o Firewall do Windows com Segurança Avançada**
2. **Selecione "Regras de Entrada" e clique em "Nova Regra..."**
3. **Selecione "Porta" e clique em "Avançar"**
4. **Selecione "TCP" e digite "4404" no campo de portas específicas**
5. **Selecione "Permitir a conexão" e avance até o final**
6. **Dê um nome como "RetroTranslatorPy" à regra**

## 4. Configuração do No-IP

1. **Verifique se o cliente No-IP está atualizado e em execução**
2. **Confirme que o domínio mdxhq.servegame.com está apontando para seu IP atual**
3. **Se necessário, atualize o cliente No-IP com suas credenciais**:
   - **Client ID**: C3A42909886
   - **IP Address**: 201.81.240.3
   - **Domain**: mdxhq.servegame.com

## 5. Teste de Acesso Externo

1. **Inicie o servidor RetroTranslatorPy**:
   ```
   python main.py
   ```

2. **Teste o acesso usando seu domínio**:
   - Em outro dispositivo (como um celular usando dados móveis, não Wi-Fi), abra um navegador
   - Acesse: `http://mdxhq.servegame.com:4404/docs`
   - Você deverá ver a documentação da API FastAPI se tudo estiver funcionando corretamente

## 6. Configuração do RetroArch em Dispositivos Remotos

Agora, para usar o serviço em outros dispositivos:

1. **Abra o RetroArch no dispositivo remoto**
2. **Settings → AI Service**
3. **Configure os seguintes parâmetros**:
   - **AI Service URL**: `http://mdxhq.servegame.com:4404`
   - **AI Service Output**: `Image Mode`
   - **Source Language**: `English` (ou idioma do jogo)
   - **Target Language**: `Portuguese` (ou idioma desejado)

## 7. Considerações de Segurança

- **Banco de dados**: Seu banco de dados MariaDB está configurado para aceitar apenas conexões locais (`host: 'localhost'`). Isso é bom para segurança.
- **Autenticação**: Considere adicionar autenticação básica ao seu serviço se ele for acessível publicamente.
- **HTTPS**: Para maior segurança, considere configurar HTTPS usando certificados Let's Encrypt.

## 8. Solução de Problemas

Se o serviço não estiver acessível externamente:

1. **Verifique se o servidor está rodando** (`python main.py`)
2. **Confirme as configurações do redirecionamento de porta**
3. **Teste se a porta está aberta** usando um serviço como [canyouseeme.org](https://canyouseeme.org/)
4. **Verifique se o domínio No-IP está atualizado** com seu IP atual
5. **Temporariamente desative o firewall** para testar se ele está bloqueando as conexões

Com essas configurações, seu serviço RetroTranslatorPy estará acessível pela internet através do domínio mdxhq.servegame.com:4404.
        