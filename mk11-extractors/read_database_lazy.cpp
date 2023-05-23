#include<iostream>
#include<fstream>
#include<sstream>
#include<iomanip>
#include<cstring>
using namespace std;

ifstream fin;
unsigned long int read_counter = 0;

int read_little(unsigned char);
string read_string(unsigned int);

void get_guid(unsigned int*);

void skip(unsigned int);
void save(unsigned int, unsigned int);
void print(unsigned long int v)
{
    cout<<hex<<left<<v<<endl;
}

void print_long(unsigned int* v, int size)
{
    for (int i = 0; i < size; i++)
    {
        cout<<hex<<right<<setfill('0')<<setw(8)<<v[i];
    }
    cout<<endl;
}

unsigned char name_values[4];

void get_names()
{
    ifstream file("database\\names.txt");
    string name;
    int line_ctr = 0;;
    while(getline(file, name))
    {
        if (!strcmp(name.c_str(), "Guid"))
        {
            name_values[0] = line_ctr;
        }
        else if (!strcmp(name.c_str(), "StructProperty"))
        {
            name_values[1] = line_ctr;
        }
        else if (!strcmp(name.c_str(), "Name"))
        {
            name_values[2] = line_ctr;
        }
        else if (!strcmp(name.c_str(), "StrProperty"))
        {
            name_values[3] = line_ctr;
        }
        line_ctr++;
    }
    file.close();
}


string get_values_type(unsigned char* v)
{
    unsigned char h[16] = {name_values[0], 00, 00, 00, 00, 00, 00, 00, name_values[1], 00, 00, 00, 00, 00, 00, 00};
    unsigned char n[16] = {name_values[2], 00, 00, 00, 00, 00, 00, 00, name_values[3], 00, 00, 00, 00, 00, 00, 00};
    bool eq = true;

    for (int i = 0; i < 16; i++)
    {
        if (v[i] != h[i])
        {
            eq = false;
            break;
        }
    }

    if (eq)
        return "guid";

    eq = true;

    for (int i = 0; i < 16; i++)
    {
        if (v[i] != n[i])
        {
            eq = false;
            break;
        }
    }

    if (eq)
        return "name";

    return "none";
}


int main(int argv, const char* argc[])
{
    string fname;
    if (argv > 1)
        fname = argc[1];
    else return -1;
    get_names();
    fin.open(fname.c_str(), ios::binary);
    fin>>noskipws;

    unsigned char c;
    unsigned int unk;
    unsigned int ignore;
    unk = read_little(4);
    //cout<<hex<<left<<unk<<endl;


    unsigned char values[16];
    for (int i = 0; i < 16; i++)
    {
        fin>>values[i];
        read_counter++;
    }
    //cout<<dec<<read_counter<<endl;
    //cout<<fin.peek()<<endl;
    while(fin.peek() != EOF)
    {
        string values_type = get_values_type(values);
        bool found = false;
        if (values_type == "name")
        {
            read_little(8);
            unsigned int name_len = read_little(4);
            string name = read_string(name_len);
            found = true;
            cout<<"Name: "<<name<<endl;
        }
        else if (values_type == "guid")
        {
            read_little(16);
            unsigned int guid[4];
            get_guid(guid);
            cout<<"GUID: ";
            print_long(guid, 4);
            found = true;
        }
        if (!found)
        {
            for (int i = 0; i < 15; i++)
            {
                values[i] = values[i+1];
            }
            fin>>values[15];
            read_counter++;

        }
        else
        {
            for (int i = 0; i < 16; i++)
            {
                fin>>values[i];
                read_counter++;
            }
        }

    }






}

int read_little(unsigned char size)
{
    unsigned char H[20];
    for (int i = 0; i < size; i++)
    {
        fin>>H[i];
        read_counter++;
    }
    unsigned int x = 0;

    for (int i = 0; i < size; i++)
    {
        if (i)
            x <<= 8;
        x |= H[size-i-1];

    }
    return x;
}

void skip(unsigned int skip_to)
{
    while (read_counter < skip_to)
        read_little(1);
}

void save(unsigned int save_to, unsigned int index)
{
    stringstream ss("");
    ss<<"data\\output_"<<index<<".seg";
    ofstream fout;
    fout.open(ss.str().c_str(), ios::binary);

    while(read_counter < save_to)
    {
        fout<<(unsigned char)(read_little(1));
    }
}

string read_string(unsigned int size)
{
    string s = "";
    unsigned char x;
    for (int i = 0; i < size -1; i++)
    {
        fin>>x;
        s += x;
        read_counter++;
    }
    fin>>x;
    read_counter++;
    return s;
}

void get_guid(unsigned int* guid)
{
    for (int i = 0; i < 4; i++)
    {
        guid[i] = read_little(4);
    }
}
