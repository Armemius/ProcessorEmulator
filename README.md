# Архитектура Компьютера. Лабораторная работа №3

Степанов Арсений Алексеевич, P3309 (бывш. P3209)

```text
asm | stack | neum | hw | instr | struct | trap -> stream | mem | cstr | prob5 | spi
```

Базовый вариант:

```text
asm | stack | neum | hw | instr | struct | trap | mem | cstr | prob5
```

Упрощённый вариант:

```text
asm | stack | neum | hw | instr | struct | stream | mem | cstr | prob5
```

Данная реализация удовлетворяет требованиям как базового варианта, так и 
упрощённого, так как работа с устройствами ввода-вывода на программном 
уровне может осуществляться как по прерываниям, так и без них.

## Язык программирования

В варианте задания предлагается написать транслятор для ассемблер-подобного
языка.
При разработке синтаксиса и семантики учитывались особенности архитектуры
процессора.

### Описание синтаксиса в форме Бэкуса-Наура

```text
<program> ::= <statement> | <statement> <endl> <program>

<statement> ::= <declaration> | <comment> | <declaration> <comment>

<declaration> ::= <instruction> | <section> | <label> | <label> <instruction>

<instruction> ::= <opcode> | <opcode> <operands>

<operands> ::= <operand> | <operand> ',' <operands>

<operand> ::= <identifier> | <immediate>

<immediate> ::= <number> | <char> | <string>

<section> ::= '.section' <section_identifier>

<section_identifier> ::= 'text' | 'data' | 'devices'

<label> ::= <identifier> ':'

<comment> ::= ';' <string>

<opcode> ::= 'push' | 'pop' | 'inc' | 'dec' | 'swap' | 'dup' | 'nop' | 'jmp' |
             'call' | 'ret' | 'halt' | 'iret' | 'ei' | 'di' | 'in' | 'out' |
             'add' | 'sub' | 'mul' | 'div' | 'and' | 'or' | 'xor' | 'not' | 
             'neg' | 'ld' | 'st' | 'cmp' | 'jz' | 'je' | 'jnz' | 'jg' | 
             'jge' | 'jl' | 'jle' | 'res' | 'byte' | 'char' | 'str' | 'shl' 
             | 'shr' | 'rol' | 'ror' | 'addr'

<number> ::= <digit> | <digit> <number>

<digit> ::= '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'

<char> ::= "'" <character> "'"

<character> ::= <letter> | <digit> | <symbol>

<string> ::= '"' <characters> '"'

<characters> ::= <character> | <character> <characters>

<identifier> ::= <letter> | <identifier> <letter> | <identifier> <digit>

<letter> ::= 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i' | 'j' | 'k' 
             | 'l' | 'm' | 'n' | 'o' | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v' 
             | 'w' | 'x' | 'y' | 'z' | 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' 
             | 'H' | 'I' | 'J' | 'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q' | 
             'R' | 'S' | 'T' | 'U' | 'V' | 'W' | 'X' | 'Y' | 'Z'

<symbol> ::= '!' | '@' | '#' | '$' | '%' | '^' | '&' | '*' | '(' | ')' | '-' 
             | '+' | '=' | '{' | '}' | '[' | ']' | ':' | ';' |

<endl> ::= '\n' | '\n\r'
```

### Описание семантики

#### Описание команд

- `push [number | label]` -- помещает значение на вершину стека.
- `pop` -- извлекает значение со стека.
- `pushf` -- помещение регистра состояния на стек
- `popf` -- снятие и запись со стека содержимого регистра состояния
- `inc` -- увеличивает значение на вершине стека на 1.
- `dec` -- уменьшает значение на вершине стека на 1.
- `swap` -- меняет местами два значения на вершине стека.
- `dup` -- дублирует значение на вершине стека.
- `nop` -- ничего не делает, команда для отладки.
- `call [label]` -- вызов подпрограммы.
- `ret` -- возврат из подпрограммы, переход по адресу лежащему на вершине стека
  и извлечение операнда из него.
- `halt` -- завершение программы.
- `iret` -- завершение обработки прерывания, возврат из прерывания.
- `ei` -- разрешение прерываний.
- `di` -- запрет прерываний.
- `add` -- сложение двух верхних элементов стека и запись результата на вершину
  стека, операнды убираются со стека.
- `sub` -- вычитание второго элемента стека сверху из первого и запись
  результата на вершину стека, операнды убираются
  со стека.
- `mul` -- умножение двух верхних элементов стека и запись результата на вершину
  стека, операнды убираются со стека.
- `div` -- целочисленное деление второго элемента стека сверху на первый и
  запись результата на вершину стека, операнды
  убираются со стека.
- `and` -- побитовое И двух верхних элементов стека и запись результата на
  вершину стека, операнды убираются со стека.
- `or` -- побитовое ИЛИ двух верхних элементов стека и запись результата на
  вершину стека, операнды убираются со стека.
- `xor` -- побитовое исключающее ИЛИ двух верхних элементов стека и запись
  результата на вершину стека, операнды
  убираются со стека.
- `not` -- побитовое отрицание верхнего элемента стека и запись результата на
  вершину стека, операнд убирается со стека.
- `neg` -- арифметическое отрицание верхнего элемента стека и запись результата
  на вершину стека, операнд убирается со
  стека.
- `shl` -- побитовый сдвиг верхнего элемента стека влево и замена вершины стека
  на полученное значение.
- `shr` -- побитовый сдвиг верхнего элемента стека вправо и замена вершины стека
  на полученное значение.
- `rol` -- циклический сдвиг верхнего элемента стека влево и замена вершины
  стека на полученное значение.
- `ror` -- циклический сдвиг верхнего элемента стека вправо и замена вершины
  стека на полученное значение.
- `ld` -- загрузка из памяти ячейки по адресу, записанному в вершине и запись
  содержимого на вершину стека, операнды
  убираются со стека.
- `st` -- сохранение в память второго значения от вершины стека по адресу
  первого.
- `cmp` -- вычитание второго элемента стека сверху из первого и запись
  результата на вершину стека, операнды не
  убираются со стека.
- `jmp [label]` -- безусловный переход.
- `jz [label]` -- переход, если значение на вершине стека равно нулю, значение
  убирается с вершины стека.
- `je [label]` -- переход, если значение на вершине стека равно нулю, значение
  убирается с вершины стека.
- `jnz [label]` -- переход, если значение на вершине стека не равно нулю,
  значение убирается с вершины стека.
- `jg [label]` -- переход, если значение на вершине стека больше нуля, значение
  убирается с вершины стека.
- `jge [label]` -- переход, если значение на вершине стека больше или равно
  нулю, значение убирается с вершины стека.
- `jl [label]` -- переход, если значение на вершине стека меньше нуля, значение
  убирается с вершины стека.
- `jle [label]` -- переход, если значение на вершине стека меньше или равно
  нулю, значение убирается с вершины стека.
- `res [number]` -- резервирование N байтов в памяти.
- `byte [byte 1] (, byte 2(, byte 3 ...))` -- запись набора байтов в память.
- `char [char 1] (, char 2(, char 3 ...))` -- запись строковых литералов в
  память.
- `str [string]` -- запись строки в память.

#### Особенности реализации

Программа состоит из нескольких секций:

- Секция `text` содержит исполняемый код, в этой секции нельзя использовать
  команды резервирования памяти.
- Секция `data` содержит данные для программы, в этой секции можно использовать
  команды резервирования памяти.

Секции определяется от объявления до конца файла или следующего объявления
секции, по умолчанию файл полностью является
секцией `text`.

Программа организована в виде последовательности инструкций. Инструкции
выполняются последовательно, одна за другой.
Каждая инструкция может не содержать операндов или
содержать один, или несколько операндов.

##### Комментарии

Комментарии начинаются с символа `;` и продолжаются до конца строки.

```asm
; sample comment 1
push 0x1337 ; sample comment 2
```

##### Числа

Числа могут записывать в шестнадцатеричной, десятичной или двоичной системе
счисления. Числа в шестнадцатеричной системе
начинаются с префикса `0x`, в двоичной с `0b`.

```asm
push 0x1337 ; hexadecimal
push 0b1010 ; binary
push 42     ; decimal
```

##### Строки

Формат строк - C-style, конец строки обозначается нуль-терминатором.

Строки заключаются в двойные кавычки, нуль-терминатор не ставится автоматически,
необходимо явно его прописывать.

```asm
.section data

sample_string_1:
    str "Hello, world!\0"
    ; null terminator is added in string declaration
sample_string_2:
    str "Hello, world!"
    byte 0
    ; null terminator is added via appended zero byte
sample_string_3:
    byte 61, 62, 63, 0
    ; "abc\0" string declaration via bytes sequence
```

##### Области видимости

Операции со стеком можно выполнять из любой точки программы, определение данных
осуществляется только в секции `data`,
видимость меток глобальная.

##### Память

- Память распределяется статически на этапе трансляции
- При определении данных в секции `data` память выделяется по адресу метки и
  последующие данные записываются в память по
  порядку,
  при заполнении ячейки памяти, запись продолжается со следующей ячейки. При
  определении новой метки память выделяется
  со следующего свободного адреса.
- Порядок данных в памяти - big-endian

```asm
.section data

.string:
    str "abc\0"
.array_1:
    byte 0x12, 0x34, 0x5
.array_1:
    byte 0x1, 0x3, 0x3, 0x7

; Вид памяти после трансляции
; (условное представление в 16-разрядной сетке)
;
; +------+--------+------------------+
; | ADDR | VALUE  |     COMMENT      |
; +------+--------+------------------+
; | 0xN0 | 0x6162 | <- метка string  |
; | 0xN1 | 0x6300 |                  |
; | 0xN2 | 0x1234 | <- метка array_1 |
; | 0xN3 | 0x0500 |                  |
; | 0xN4 | 0x0103 | <- метка array_2 |
; | 0xN5 | 0x0307 |                  |
; +------+--------+------------------+
```

##### Типизация, виды литералов

Литералы могут быть представлены в виде чисел и меток, метки впоследствии
конвертируются в адреса и интерпретируются
как числа. Все строковые литералы на моменте трансляции кодируются при помощи
таблицы ASCII и интерпретируются как
числа.
Типизация отсутствует и пользователь может работать с данными в зависимости от
его интерпретации и выполнять с ними
любые
операции без каких-либо ограничений.

## Организация памяти

- Архитектура Фон-Неймана
- Линейное адресное пространство
- 16'777'216 (0x1000000) ячеек памяти, каждая ячейка размером 4 байта (32 бит),
  64Мб в сумме
- Инструкции, данные, векторы прерываний, их обработчики и подпрограммы
  находятся в одном адрессном пространстве
- Взаимодействие с данными осуществляется через стек и операции
  загрузки/сохранения (`ld`/`st`) в память
- Стек хранится в одном адресном пространстве с инструкциями и данными
- Стек растет в сторону уменьшения адресов начинаю с адреса `0x1000000`
- Адресация может быть прямой абсолютной и косвенной:
  - Прямая абсолютная адресация - адрес явно указан в инструкции
  - Косвенная адресация - адрес рассчитывается по сдвигу относительно текущей
    команды, используя значение счётчика
    команд
- Динамически считываемые данные можно помещать на стек, либо в заранее
  зарезервированный буфер
- Инициализация устройств находится в начале адресной сетки, занимает по две
  ячейки памяти на устройство и имеет следующий формат
  - Вторая ячейка -- 8 бит для флагов состояния и 24 бита адрес обработчика
    прерывания
  - Первая ячейка -- 8 бит для указания размера буфера и 24 бита для адреса
    буфера для ввода/вывода устройства
  - Флаги содержат информацию о том используются ли прерывания для устройства,
    включено ли устройство и его готовность
    - 1-й бит -- флаг работы устройства
    - 2-й бит -- флаг прерывания
    - 3-15й биты -- зарезервированы
    - Старший бит -- флаг готовности устройства

```text
       Memory
+--------------------------------------+
| 0x00 : flags and handler for dev0    |
| 0x01 : buffer size & ref for dev0    |
|   ...                                |
| 0x1E : flags and handler for dev15   |
| 0x1F : buffer size & ref for dev15   |
|   ...                                |
| 0x20 : section data : reserved data  |
|   ...                                |
| N    : section text : instructions   |
|   ...                                |
+--------------------------------------+
```

### Регистры

Процессор не имеет регистров общего назначения, так как является стековым, все
необходимые данные для его работы
хранятся на стеке.

Процессор имеет следующие специальные регистры:

- `IR` -- регистр ввода (Input Register), размер 32 бита

> Регистр для ручного ввода/вывода данных в/из регистров, предназначен для
> отладки и тестирования.

- `PC` -- счётчик команд (Program Counter), размер 24 бита

> Содержит адрес текущей выполняемой команды

- `SP` -- указатель на вершину стека (Stack Pointer), размер 24 бита

> Содержит адрес текущей вершины стека

- `CR` -- регистр команды (Command Register), размер 32 бита

> Содержит код команды для последующей дешифровки и исполнения

- `AR` -- регистр адреса (Address Register), размер 24 бита

> Содержит адрес для доступа к памяти, по этому адресу производится чтение и
> запись данных из памяти

- `DR` -- регистр данных (Data Register), размер 32 бита

> Содержит данные для записи в память или результат чтения из памяти

- `SR` -- регистр состояния (State Register), размер 16 бит

> Содержит флаги состояния процессора (флаг работы, прерывания и т.п.)
> Старший бит -- флаг работы процессора
> Бит перед старшим -- флаг прерывания
> Младшая тетрада -- флаги NZVC (Negative, Zero, Overflow, Carry)
> Остальные биты -- зарезервированы

- `BR` -- буферный регистр (Buffer Register)

> Используется для промежуточного хранения данных для операций

## Система команд

Особенности процессора:

- Машинное слова -- 32 бита (4 байта)
- Доступ к памяти осуществляется через регистры `AR` - указатель на адрес в
  памяти и `DR` - регистр содержащий данные
  для записи или результат чтения
- Устройства ввода-вывода пронумерованы от 0 до 15, работа с устройством
  происходит через команды `in` и `out` по номеру
  порта
- Поток управления:
  - Инкрементирование счётчика команд
  - Загрузка команды из памяти в командный регистр
  - Условный или безусловный переход / Выполнение команды
  - Если флаг работы в регистре состояния установлен, то продолжить
  - Проверка на то что прерывания включены, если включены, то проверка на
    наличие прерывания и уход в обработку
    прерывания
  - Перейти к выполнению следующей команды

| Команда                                                            | Стек до исполнения                                                                   | Стек после исполнения                                                              | Описание                                                                                                |
|--------------------------------------------------------------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| PUSH                                                               | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>       | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>   | Поместить значение на стек                                                                              |
| POP                                                                | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>     | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>     | Убрать значение со стека                                                                                |
| PUSHF                                                              | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>       | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>flags</td></tr></table>   | Поместить значение регистра состояния на стек                                                           |
| POPF                                                               | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>flags</td></tr></table>     | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>     | Восстановить значение регистра состояния со стека                                                       |
| INC <br> DEC <br> NEG <br> NOT <br> SHL <br> SHR <br> ROL <br> ROR | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>     | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>res</td></tr></table>     | Выполнение унарной операции над вершиной стека и помещение результата в стек заместо операнда           |
| SWAP                                                               | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>           | <table><tr><td>...</td></tr><tr><td>b</td></tr><tr><td>a</td></tr></table>         | Поменять местами два верхних элемента на стеке                                                          |
| DUP                                                                | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>a</td></tr></table>         | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>a</td></tr></table>         | Продублировать значение, находящееся на вершине стека                                                   |
| NOP                                                                | -                                                                                    | -                                                                                  | Пустая команда                                                                                          |
| CALL                                                               | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>       | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>address</td></tr></table> | Перейти в подпрограмму и сохранить адрес возврата на стек                                               |
| RET                                                                | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>address</td></tr></table>   | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>     | Возврат из подпрограммы, извлечение адреса с вершины стека и переход по нему                            |
| HALT                                                               | -                                                                                    | -                                                                                  | Снятие флага работы в регистре состояния                                                                |
| IRET                                                               | <table><tr><td>...</td></tr><tr><td>address</td></tr><tr><td>flags</td></tr></table> | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>     | Возврат из прерывания, извлечение адреса с вершины стека и переход по нему                              |
| EI                                                                 | -                                                                                    | -                                                                                  | Включить прерывания                                                                                     |
| DI                                                                 | -                                                                                    | -                                                                                  | Отключить прерывания                                                                                    |
| ADD <br> SUB <br> MUL <br> DIV <br> AND <br> OR <br> XOR           | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>           | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>res</td></tr></table>     | Выполнение бинарной операции над вершиной стека и помещение результата в стек заместо операнда          |
| ADD <br> SUB <br> MUL <br> DIV <br> AND <br> OR <br> XOR           | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>           | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>res</td></tr></table>     | Выполнение бинарной операции над вершиной стека и помещение результата в стек заместо операнда          |
| LD                                                                 | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>addr</td></tr></table>      | <table><tr><td>...</td></tr><tr><td>value</td></tr><tr><td>addr</td></tr></table>  | Прочитать значение ячейки по адресу из вершины стека и добавить его на вершину стека                    |
| ST                                                                 | <table><tr><td>...</td></tr><tr><td>value</td></tr><tr><td>addr</td></tr></table>    | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>addr</td></tr></table>    | Сохранить значение вершины стека по адресу из второго сверху элемента, убрать верхний элемент со стека  |
| CMP                                                                | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>           | <table><tr><td>res</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>         | Вычесть второй элемент сверху стека из первого и добавить результат на вершину стека                    |
| JMP                                                                | -                                                                                    | -                                                                                  | Безусловный переход                                                                                     |
| JG <br> JGE <br> JL <br> JLE <br> JE <br> JZ                       | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>     | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>     | Условный переход если верхний элемент со стека удовлетворяет условию, снятие верхнего элемента со стека |
| BYTE <br> CHAR <br> STR                                            | -                                                                                    | -                                                                                  | Псевдокоманды для выделения памяти в секции data                                                        |

### Формат инструкций

Формат адресных и безадресных инструкций различается:

- Адресные:
  - 6 бит -- Код операции
  - 2 бита -- Режим адресации
    - 0b00 -- прямая адресация
    - 0b01 -- косвенная адресация
    - 0b10 -- прямая загрузка
  - 24 бита -- Адрес, сдвиг (24 бит) или значение (16 младших бит)
- Безадресные:
  - 8 бит -- Код операции
  - 24 бит -- Данные для команды

У безадресных команд старший бит всегда равен нулю, у адресных -- единице.

Коды и формат операций:

### Адресные инструкции

| Код  | Мнемоника | Формат операции                          |
|------|-----------|------------------------------------------|
| 0x80 | JMP       | 6 бит код, 2 бита режима, 24 бита адреса |
| 0x84 | JZ        | 6 бит код, 2 бита режима, 24 бита адреса |
| 0x88 | JE        | 6 бит код, 2 бита режима, 24 бита адреса |
| 0x8B | JNZ       | 6 бит код, 2 бита режима, 24 бита адреса |
| 0x90 | JG        | 6 бит код, 2 бита режима, 24 бита адреса |
| 0x94 | JGE       | 6 бит код, 2 бита режима, 24 бита адреса |
| 0x98 | JL        | 6 бит код, 2 бита режима, 24 бита адреса |
| 0x9B | JLE       | 6 бит код, 2 бита режима, 24 бита адреса |
| 0xA0 | CALL      | 6 бит код, 2 бита режима, 24 бита адреса |
| 0xA4 | PUSH      | 6 бит код, 2 бита режима, 24 бита адреса |

### Безадресные инструкции

| Код  | Мнемоника | Формат операции                          |
|------|-----------|------------------------------------------|
| 0x00 | NOP       | 8 бит код, 24 бита не используются       |
| 0x02 | POP       | 8 бит код, 24 бита не используются       |
| 0x03 | PUSHF     | 8 бит код, 24 бита не используются       |
| 0x04 | POPF      | 8 бит код, 24 бита не используются       |
| 0x05 | INC       | 8 бит код, 24 бита не используются       |
| 0x06 | DEC       | 8 бит код, 24 бита не используются       |
| 0x07 | SWAP      | 8 бит код, 24 бита не используются       |
| 0x08 | DUP       | 8 бит код, 24 бита не используются       |
| 0x09 | RET       | 8 бит код, 24 бита не используются       |
| 0x0A | HALT      | 8 бит код, 24 бита не используются       |
| 0x0C | IRET      | 8 бит код, 24 бита не используются       |
| 0x0D | EI        | 8 бит код, 24 бита не используются       |
| 0x0E | DI        | 8 бит код, 24 бита не используются       |
| 0x11 | ADD       | 8 бит код, 24 бита не используются       |
| 0x12 | SUB       | 8 бит код, 24 бита не используются       |
| 0x13 | MUL       | 8 бит код, 24 бита не используются       |
| 0x14 | DIV       | 8 бит код, 24 бита не используются       |
| 0x15 | AND       | 8 бит код, 24 бита не используются       |
| 0x16 | OR        | 8 бит код, 24 бита не используются       |
| 0x17 | XOR       | 8 бит код, 24 бита не используются       |
| 0x18 | NOT       | 8 бит код, 24 бита не используются       |
| 0x19 | NEG       | 8 бит код, 24 бита не используются       |
| 0x1A | SHL       | 8 бит код, 24 бита не используются       |
| 0x1B | SHR       | 8 бит код, 24 бита не используются       |
| 0x1C | ROL       | 8 бит код, 24 бита не используются       |
| 0x1D | ROR       | 8 бит код, 24 бита не используются       |
| 0x1E | CMP       | 8 бит код, 24 бита не используются       |
| 0x28 | LD        | 6 бит код, 2 бита режима, 24 бита адреса |
| 0x29 | ST        | 6 бит код, 2 бита режима, 24 бита адреса |

### Пример

Для исходного кода:

```asm
; Раздел данных, где инициализируется значения
.section data
number:
    byte 0x04, 0x00  ; Инициализация числа 1024 (0x0400) в памяти

; Исполнимая секция кода
.section text
    ; Загрузка значения из памяти
    push number
    ld              ; Загрузить число из метки 'number' на стек
    push 0x1337     ; Поместить число 0x1337 на стек

    ; Выполнение сложения
    add             ; Сложить два числа на вершине стека, результат оставить на стеке

    ; Очистка стека
    pop             ; Удалить результат со стека

    ; Завершение программы
    halt            ; Остановить выполнение программы
```

Инструкции представлены в текстовом формате, каждая строчка хранит адрес и
машинный код инструкции в 16-разрядном виде (
`ADDR : OPCODE`):

```text
000000: 00000400  ; Инициализация переменной number значением 1024
000004: 91FFFFFB  ; push number с косвенной адресацией, сдвиг 0x4
000005: 88000000  ; ld
000006: 01001337  ; push 0x1337
000007: 11000000  ; add
000008: 02000000  ; pop
000009: 0A000000  ; halt
```

## Транслятор

Интерфейс командной строки:

```text
usage: translator.py [-h] -s SOURCE -o OUTPUT

CSA Lab 3 assembly translator

options:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        File with asm code
  -o OUTPUT, --output OUTPUT
                        File with output opcodes
```

- Пример использования
  `python translator.py -s examples/sample.asm -o examples/sample.bin`
  - Обязательные аргументы:
    - `-s` или `--source` - путь к файлу с исходным кодом
    - `-o` или `--output` - путь к файлу с бинарным кодом
  - Необязательные аргументы:
    - `-h` или `--help` - справка

Главный модуль программы - [`translator.py`](https://github.com/Armemius/ProcessorEmulator/blob/main/src/translator/translator.py)

### Этапы трансляции

- Лексический анализ

> Разбитие исходного кода на лексические токены

- Синтаксический анализ и построение синтаксического дерева

> Проверка порядка лексем и синтаксических конструкций, построение
> синтаксического дерева

- Семантический анализ

> Проверка семантики программы, проверка соответствия количества аргументов и
> типов данных для каждой инструкции

- Генерация кода

> Преобразование синтаксического дерева в машинный код, вычисление адресов
> меток, упорядочивание секций data и text в
> памяти

### Правила

- Дублирующиеся метки запрещены
- В секции `data` можно использовать только псевдокоманды `res`,`byte`, `char` и
  `str` для выделения и инициализации
  памяти
- Программа должна определять точку входа через метку `start` в секции `text`

### Особенности

- Инициализация устройств происходит в начале адресного пространства, до адреса
  `0x1F`
- Секция `data` начинается с адреса `0x20`
- Секция `text` имеет отступ в 16 ячеек памяти от секции `data`
- Все данные вне зависимости от положения в исходном коде размещаются в секции
  `data` в порядке объявления до секции
  `text`
  в результирующем машинном коде
- Все определённые метки являются глобальными
- Обращение к мнемонике инструкции регистронезависимо
- По умолчанию файл является секцией `text`

## Модель процессора

Интерфейс командной строки:

```text
usage: emulator.py [-h] -o SOURCES

CSA Lab 3 emulator

options:
  -h, --help            show this help message and exit
  -o SOURCES, --sources SOURCES
                        File with operation codes
  -i INPUT, --input INPUT
                        File with input data queue
```

- Пример использования
  `python emulator.py -o examples/sample.bin`
  - Обязательные аргументы:
    - `-o` или `--sources` - путь к файлу с бинарным кодом
  - Необязательные аргументы:
    - `-h` или `--help` - справка
    - `-i` или `--input` - путь к файлу с входными данными для устройств ввода
    - `-n` или `--interrupt` - использование ввода данных по прерываниям

### Схема `data path`

![Data path](./assets/data_path.png)

### Схема `control unit`

![Control unit](./assets/control_unit.png)

## Тестирование

Тестирование выполняется при помощи подхода golden test

При обновлении файлов в репозитории запускается задание `GitHub Actions`, 
которое прогоняет проект через тесты и линтеры:

- задание `test` -- проверка кода через golden test'ы
- задание `lint-python` -- проверка кода через `flake8`
- задание `lint-markdown` -- проверка документации через `markdownlint`

### CI при помощи Github Action

```yaml
name: ProcessorEmulator

on:
  push:
    branches: [ "main", "dev" ]
  pull_request:
    branches: [ "main", "dev" ]

jobs:
  lint-markdown:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Install markdownlint-cli
        run: |
          npm install -g markdownlint-cli

      - name: Lint Markdown files
        run: |
          markdownlint '**/*.md'

  lint-python:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install flake8
        run: |
          python -m pip install --upgrade pip
          pip install flake8

      - name: Lint Python files
        run: |
          flake8 .

  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest
          pip install pytest-timeout

      - name: Test
        run: |
          pytest
```

### Результаты тестирования

Тестирование осуществляется при помощи утилиты `pytest` и `pytest-timeout`, 
результаты выполнения теста:

```text
(.venv) PS C:\Users\armemius\Documents\projects\csa-lab-3> pytest
======================================================================================================= test session starts =======================================================================================================
platform win32 -- Python 3.10.11, pytest-8.3.3, pluggy-1.5.0
rootdir: C:\Users\armemius\Documents\projects\csa-lab-3
plugins: timeout-2.3.1
collected 4 items                                                                                                                                                                                                                  

test\golden_test.py ....                                                                                                                                                                                                     [100%]

======================================================================================================== 4 passed in 1.92s ======================================================================================================== 
```

### Программы, используемые для тестирования

#### Hello World

```nasm
.section devices
dev0:
        byte 0x81
        addr null
        byte 0x10
        addr buffer_0
dev1:
        byte 0x81
        addr null
        byte 0x10
        addr buffer_0

.section data
buffer_0:
        str "Hello, World!"
        byte 0x0

.section text
start:
    halt
``` 

Вывод программы: 

```text
> Hello, World!
```

Журнал работы:

```text
Tick: 37 	| Instruction: 1   | PC: 000034 | SP: 000000 | CR: F0000002 | AR: 000002 | DR: 81000000 | SR: 8008 | BR: 00000002 | TOS: 81000000 | NOS: 10000020
Tick: 42 	| Instruction: 2   | PC: 000035 | SP: 000000 | CR: 0A000000 | AR: 000034 | DR: 0A000000 | SR: 0008 | BR: 00000034 | TOS: 81000000 | NOS: 10000020

```

#### Cat

```nasm
.section devices
dev0:
        byte 0x81
        addr null
        byte 0xFF
        addr buffer_0
dev1:
        byte 0x01
        addr null
        byte 0xFF
        addr buffer_0

.section data
buffer_0:
        res 0xFF

.section text
start:
    unset dev0
    check dev0
    jz end
    set dev1
    jmp start

end:
    halt
```

Вывод программы: 

```text
< Hello, World!
> Hello, World!
< I
> I
< love
> love
< CSA
> CSA
< Lab3
> Lab3
```

Журнал работы:

```text
Tick: 40 	| Instruction: 1   | PC: 000071 | SP: 000000 | CR: F4000000 | AR: 000000 | DR: 01000000 | SR: 8000 | BR: 00000000 | TOS: 81000000 | NOS: FF000020
Tick: 70 	| Instruction: 2   | PC: 000072 | SP: 000000 | CR: FC000000 | AR: FFFFFE | DR: 80000000 | SR: 8008 | BR: 80000000 | TOS: 81000000 | NOS: FF000020
Tick: 74 	| Instruction: 3   | PC: 000073 | SP: 000000 | CR: 84000075 | AR: 000072 | DR: 84000075 | SR: 8008 | BR: 00000072 | TOS: 81000000 | NOS: FF000020
Tick: 111 	| Instruction: 4   | PC: 000074 | SP: 000000 | CR: F0000002 | AR: 000002 | DR: 81000000 | SR: 8008 | BR: 00000002 | TOS: 81000000 | NOS: FF000020
Tick: 116 	| Instruction: 5   | PC: 000070 | SP: 000000 | CR: 80000070 | AR: 000074 | DR: 80000070 | SR: 8008 | BR: 00000074 | TOS: 81000000 | NOS: FF000020
Tick: 156 	| Instruction: 6   | PC: 000071 | SP: 000000 | CR: F4000000 | AR: 000000 | DR: 01000000 | SR: 8000 | BR: 00000000 | TOS: 81000000 | NOS: FF000020
Tick: 186 	| Instruction: 7   | PC: 000072 | SP: 000000 | CR: FC000000 | AR: FFFFFE | DR: 80000000 | SR: 8008 | BR: 80000000 | TOS: 81000000 | NOS: FF000020
Tick: 190 	| Instruction: 8   | PC: 000073 | SP: 000000 | CR: 84000075 | AR: 000072 | DR: 84000075 | SR: 8008 | BR: 00000072 | TOS: 81000000 | NOS: FF000020
Tick: 227 	| Instruction: 9   | PC: 000074 | SP: 000000 | CR: F0000002 | AR: 000002 | DR: 81000000 | SR: 8008 | BR: 00000002 | TOS: 81000000 | NOS: FF000020
Tick: 232 	| Instruction: 10   | PC: 000070 | SP: 000000 | CR: 80000070 | AR: 000074 | DR: 80000070 | SR: 8008 | BR: 00000074 | TOS: 81000000 | NOS: FF000020
Tick: 272 	| Instruction: 11   | PC: 000071 | SP: 000000 | CR: F4000000 | AR: 000000 | DR: 01000000 | SR: 8000 | BR: 00000000 | TOS: 81000000 | NOS: FF000020
Tick: 302 	| Instruction: 12   | PC: 000072 | SP: 000000 | CR: FC000000 | AR: FFFFFE | DR: 80000000 | SR: 8008 | BR: 80000000 | TOS: 81000000 | NOS: FF000020
Tick: 306 	| Instruction: 13   | PC: 000073 | SP: 000000 | CR: 84000075 | AR: 000072 | DR: 84000075 | SR: 8008 | BR: 00000072 | TOS: 81000000 | NOS: FF000020
Tick: 343 	| Instruction: 14   | PC: 000074 | SP: 000000 | CR: F0000002 | AR: 000002 | DR: 81000000 | SR: 8008 | BR: 00000002 | TOS: 81000000 | NOS: FF000020
Tick: 348 	| Instruction: 15   | PC: 000070 | SP: 000000 | CR: 80000070 | AR: 000074 | DR: 80000070 | SR: 8008 | BR: 00000074 | TOS: 81000000 | NOS: FF000020
Tick: 388 	| Instruction: 16   | PC: 000071 | SP: 000000 | CR: F4000000 | AR: 000000 | DR: 01000000 | SR: 8000 | BR: 00000000 | TOS: 81000000 | NOS: FF000020
Tick: 418 	| Instruction: 17   | PC: 000072 | SP: 000000 | CR: FC000000 | AR: FFFFFE | DR: 80000000 | SR: 8008 | BR: 80000000 | TOS: 81000000 | NOS: FF000020
Tick: 422 	| Instruction: 18   | PC: 000073 | SP: 000000 | CR: 84000075 | AR: 000072 | DR: 84000075 | SR: 8008 | BR: 00000072 | TOS: 81000000 | NOS: FF000020
Tick: 459 	| Instruction: 19   | PC: 000074 | SP: 000000 | CR: F0000002 | AR: 000002 | DR: 81000000 | SR: 8008 | BR: 00000002 | TOS: 81000000 | NOS: FF000020
Tick: 464 	| Instruction: 20   | PC: 000070 | SP: 000000 | CR: 80000070 | AR: 000074 | DR: 80000070 | SR: 8008 | BR: 00000074 | TOS: 81000000 | NOS: FF000020
Tick: 504 	| Instruction: 21   | PC: 000071 | SP: 000000 | CR: F4000000 | AR: 000000 | DR: 01000000 | SR: 8000 | BR: 00000000 | TOS: 81000000 | NOS: FF000020
Tick: 534 	| Instruction: 22   | PC: 000072 | SP: 000000 | CR: FC000000 | AR: FFFFFE | DR: 80000000 | SR: 8008 | BR: 80000000 | TOS: 81000000 | NOS: FF000020
Tick: 538 	| Instruction: 23   | PC: 000073 | SP: 000000 | CR: 84000075 | AR: 000072 | DR: 84000075 | SR: 8008 | BR: 00000072 | TOS: 81000000 | NOS: FF000020
Tick: 575 	| Instruction: 24   | PC: 000074 | SP: 000000 | CR: F0000002 | AR: 000002 | DR: 81000000 | SR: 8008 | BR: 00000002 | TOS: 81000000 | NOS: FF000020
Tick: 580 	| Instruction: 25   | PC: 000070 | SP: 000000 | CR: 80000070 | AR: 000074 | DR: 80000070 | SR: 8008 | BR: 00000074 | TOS: 81000000 | NOS: FF000020
Tick: 620 	| Instruction: 26   | PC: 000071 | SP: 000000 | CR: F4000000 | AR: 000000 | DR: 01000000 | SR: 8000 | BR: 00000000 | TOS: 01000000 | NOS: FF000020
Tick: 650 	| Instruction: 27   | PC: 000072 | SP: 000000 | CR: FC000000 | AR: FFFFFE | DR: 00000000 | SR: 8004 | BR: 80000000 | TOS: 01000000 | NOS: FF000020
Tick: 655 	| Instruction: 28   | PC: 000075 | SP: 000000 | CR: 84000075 | AR: 000072 | DR: 84000075 | SR: 8004 | BR: 00000072 | TOS: 01000000 | NOS: FF000020
Tick: 660 	| Instruction: 29   | PC: 000076 | SP: 000000 | CR: 0A000000 | AR: 000075 | DR: 0A000000 | SR: 0004 | BR: 00000075 | TOS: 01000000 | NOS: FF000020
```

## Статистика по алгоритмам

```text
| ФИО                          | алг            | LoC | code инстр. | инстр.  | такт.  |
| Степанов Арсений Алексеевич  | hello_world    | 21  | 2           | 2       | 41     |
| Степанов Арсений Алексеевич  | hello_username | 267 | 197         | 2421    | 22034  |
| Степанов Арсений Алексеевич  | cat            | 27  | 6           | 29      | 660    |
| Степанов Арсений Алексеевич  | prob5          | 228 | 146         | 7440    | 68469  |
```