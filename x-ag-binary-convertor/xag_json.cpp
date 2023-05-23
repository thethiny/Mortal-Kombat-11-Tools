#include<iostream>
#include<fstream>
#include<stack>
#include<cstring>
using namespace std;

ifstream fin;
ofstream fout;

void read_value(bool = 0, bool = 0);
void read_list(bool, unsigned char);
long long _to_int(unsigned char [], unsigned char power);
double _to_float(unsigned char [], unsigned char power);
long int indent = 0;
void write_indent()
{
    for (int i = 0; i < indent; i++)
    {
        fout<<"    ";
    }
}

void read_list(bool t, unsigned char c)
{
    unsigned char A[8];
    indent += 1;
    if (t)
    {
        fout<<"{\n";
        write_indent();
    }
    else
    {
        fout<<"[\n";
        write_indent();
    }

    unsigned char _to = c & 0b00001111;
    unsigned char i;
    for (i = 0; i < _to+1; i++)
    {
        fin>>A[i];
    }
    long long __to = _to_int(A, i);

    for (long long i = 0; i < __to; i++)
    {
        if (i)
        {
            fout<<",\n";
            write_indent();
        }
        read_value(false, !t);
    }

    if (t)
    {
        indent -= 1;
        fout<<"\n";
        write_indent();
        fout<<"}";
    }
    else
    {
        indent -= 1;
        fout<<"\n";
        write_indent();
        fout<<"]";
    }


}

void read_value(bool t, bool single)
{
    unsigned char c, A[8];

    fin>>c;
    if (c == 0x10)
    {
        fin>>A[0];

        fout<<_to_int(A, 1);
    }
    if (c == 0x11)
    {
        fin>>A[0];

        fout<<(unsigned long long)(_to_int(A, 1));
    }
    else if (c == 0x12)
    {
        for (int i = 0; i < 2; i++)
        {
            fin>>A[i];
        }
        fout<<_to_int(A, 2);
    }
    else if (c == 0x13)
    {
        for (int i = 0; i < 2; i++)
        {
            fin>>A[i];
        }
        fout<<(unsigned long long)(_to_int(A, 2));
    }
    else if (c == 0x14)
    {
        for (int i = 0; i < 4; i++)
        {
            fin>>A[i];
        }
        fout<<_to_int(A, 4);
    }
    else if (c == 0x15)
    {
        for (int i = 0; i < 4; i++)
        {
            fin>>A[i];
        }
        fout<<(unsigned long long)(_to_int(A, 4));
    }
    else if (c == 0x16) ///0x21 is float64
    {
        for (int i = 0; i < 8; i++)
        {
            fin>>A[i];
        }
        fout<<_to_int(A, 8);
    }
    else if (c == 0x17)
    {
        for (int i = 0; i < 8; i++)
        {
            fin>>A[i];
        }
        fout<<(unsigned long long)(_to_int(A, 8));
    }
    else if (c == 0x21)
    {
        for (int i = 0; i < 8; i++)
        {
            fin>>A[i];
        }
        fout<<_to_float(A, 8);
    }
    else if (c == 0x40) ///TIME
    {
        fout<<'"';
        for (int i = 0; i < 4; i++)
        {
            fin>>A[i];
        }
        fout<<_to_int(A, 4);
        fout<<'"';
    }
    else if (c == 0x30 || c == 0x31) ///Strings, Probably 32 is string of 4 places, or it's base64 short. I can't tell yet.
    {
        unsigned int i;
        for (i = 0; i < c-0x30 + 1; i++)
        {
            fin>>A[i];
        }
        fout<<'"';
        unsigned int _to;
        _to = _to_int(A, i);
        for (unsigned int i = 0; i < _to; i++)
        {
            fin>>c;
            fout<<c;
        }
        fout<<'"';
    }
    else if (c == 0x33 || c == 0x34)
    {
        for (int i = 0; i < c-0x32; i++)
        {
            fin>>A[i];
        }
        unsigned long long _to = _to_int(A, c-0x32);
        for (int i = 0; i < _to; i++)
        {
            if (i)
                fout<<" ";
            fin>>c;
            fout<<hex<<(unsigned int)(c)<<dec;
        }
        //fout<<"\"Not Yet Decoded Base64\"";
    }
    else if (c == 0x00) ///IDK what's this so for now it's undef
    {
        fout<<"undef";
    }
    else if (c == 0x01)
    {
        fout<<"null";
    }
    else if (c == 0x02)
    {
        fout<<"true";
    }
    else if (c == 0x03)
    {
        fout<<"false";
    }
    else if ((c >= 0x50 && c <= 0x53) || (c >= 0x60 && c <= 0x63))
    {
        if ((c - 0x50) < 0x10)
            read_list(false, c);
        else read_list(true, c);
    }

    if (!t && !(c == 0x50 || c == 0x60) && !single)
    {
        fout<<": ";
        read_value(1);
    }

}

long long _to_int(unsigned char A[], unsigned char power)
{
    long int sum = A[0];
    for (int i = 1; i < power; i++)
    {
        sum <<= 8;
        sum |= A[i];
    }

    return sum;
}

double _to_float(unsigned char A[], unsigned char power)
{
    double f;
    unsigned char b[] = {A[7], A[6], A[5], A[4], A[3], A[2], A[1], A[0]};
    memcpy(&f, &b, sizeof(f));
    return f;
}

int main(int argv, const char* argc[])
{
    string f_name = argc[1];
    string f_out_name = argc[1];
    f_out_name += ".out.json";
    fin.open(f_name.c_str(), ios::binary);
    fout.open(f_out_name.c_str(), ios::binary);
    unsigned char c;
    fin>>noskipws;
    read_value();
}
