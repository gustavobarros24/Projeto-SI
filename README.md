# Ativar o ambiente virtual

```sh
source psi/bin/activate
```

# Executar a LLM no Spark com

```sh
vllm serve '<model-id>'
```

# Abrir um tunnel para acessar a LLM localmente

```sh
./run_tunnel.sh
```

ou manualmente:

```sh
ssh -L 8008:localhost:8000 -p <porta> <user>@<server-ip>
```

## Ou abrir sem manter a sessão

```sh
ssh -N -L 8008:localhost:8000 -p <porta> <user>@<server-ip>
```

# TASKS

- [ ] Implementar o agente evaluator
- [ ] Implementar o agente narrador (voz do paciente)
- [ ] Fazer com que o Geminni sempre gere as respostas (o Output do MedGemma é passado ao geminni para responder corretamente)
- [ ] Salvar em base de dados os dados do final da sessão (pontos fracos do aluno, nível do aluno, incrementar o número de sessões que o aluno efetuou, etc.)
- [ ] **Módulo de Anamnese**: Gerar relatório estruturado final sobre a sessão (não necessáriamente em PDF, pode ser apenas em texto corrido no final da sessão.). Esse relatório é como os relatório que os médicos escrevem no pc, documentando toda a anamnese feita.

## Tarefas a serem definidas (não planejadas completamente)

- [ ] Implementar um terceiro módulo para Triagem em Urgências.
  - Temos que definir melhor com o professor como este módulo funcionará, e depois disso, definimos a pipeline, subgrafo e agentes.

## Aprimoramentos (parte final)

- [ ] Redirecionamento para inputs do estudante totalmente fora do contexto da conversa (trocar de assunto, mensagens ofensivas, etc.).
- [ ] Observabilidade com LangSmith.
- [ ] Autenticação no Frontend.
- [ ] Um utilizador pode criar múltiplos chats (sessões).
- [ ] Fazer stream das respostas das LLMs.
- [ ] Fine tuning do modelo com dados de treino fornecidos pelo professor
  - Documentação que pode ser importante para fazer fine tuning futuramente: https://www.datacamp.com/tutorial/fine-tuning-medgemma

# Referências

Documentos utilizados como referência ou material de teste ao longo do desenvolvimento.

## Casos de anamnese

- **UNC School of Medicine — Anamnesis write-up** — [`UMNwriteup.pdf`](https://www.med.unc.edu/medclerk/wp-content/uploads/sites/877/2018/10/UMNwriteup.pdf). Caso clínico real usado para testar o upload e a extração automática de campos (persona, diagnóstico, sintomas, estado emocional) pelo MedGemma no módulo de anamnese.
