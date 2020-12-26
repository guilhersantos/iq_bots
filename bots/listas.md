### GERADOR DE LISTA DE SINAIS M5

#### - Descrição

A lista será gerada baseando-se no numéro de ocorrência de um candle de alta(verde) ou de baixa(vermelho) 
em cada horário alternando-se de 5 em 5 minutos, onde será somando essa ocorrência e divida pelo número de dias.

#### - Exemplo:

> - Uma das pariedades escolhida EURUSD
> - Quantidade de dias igual a 60
> - Hora: 10:00
> - Quantidade de candles verdes igual a 30
> - Quantidade de candles vermelhos igual a 25
> - Quantidade de candles dojis igual a 5
>   - verdes/dias = 50%
>   - vermelhos/dias = 41,6%
>   - dojis/dias = 8,3% -> iguinora-se os dojis
> 
> Sinal gerado igual -> EURUSD;10:00;CALL

#### - Versões

> 1.0: As configurações se encontram dentro do código<br/>
> - Lista de pariedades: pariedades
> - Quantidade de dias: quantidade_dias
> - Filtro de percentual: filtro_percentual
