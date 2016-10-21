# robbe-b6-eq-bid-reader

read and parse messages emitted by robbe b6 eq-bid charger

# message format

The message format (as far as I was able to decode it):

```
    START LEN U_IN I_IN U_OUT I_OUT UNKNOWN_FIXED CHK_SUM?

    START: '\x0c', fixed
    LEN : ASCII coded, fixed 64 byte message length
    U_IN : hex ASCII coded UINT16 milli Volt
    I_IN : hex ASCII coded UINT16 milli Ampere
    U_OUT : hex ASCII coded UINT16 milli Volt
    I_OUT : hex ASCII coded UINT16 milli Ampere
    P_OUT: hex ASCII coded UINT16 milli Ampere hours
    UNKNOWN_FIXED: 000001000000000000000000000000000
    CHK_SUM: 3 digit hex num, ASCII encoded (not sure about that)
```

example:

```
	\x0c642FA901003DAA00C70009000001000000000000000000000000000ABA\r

	\x0c64
    2FAC - 12204 => 12.204 V
    0100 - 256 => 0.256 A
    3305 - 13061 => 13.061 V
    00C7 - 194 => 0.194 A
    0009 - 9 => 0.009 Ah
    000001000000000000000000000000000A8D\r
```

# usage

Simply call the read method of the *B6EqBidReader* instance:

```python
with B6EqBidReader() as reader:

    try:
        while True:
            print reader.read()
    except KeyboardInterrupt:
        pass
```

The returned value is of type *B6EqBidData* that offers a property for
each value contained in the charger messages:

- v_in : charger voltage input, in milli Volt
- i_in : charger current input, in milli Ampere
- v_out : charger voltage output, in milli Volt
- i_out : charger current output, in milli Ampere
- charge : electric charge, in milli Ampere hours
- time : time-stamp the message was parsed, in seconds

The string-representation of a *B6EqBidData* instance uses JSON to format the data:
```
{
    "_charge": 1,
    "_i_in": 256,
    "_i_out": 199,
    "_time": 1477085519.234749,
    "_v_in": 12177,
    "_v_out": 15700
}
```