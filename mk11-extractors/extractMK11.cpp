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

void skip(unsigned int);
void save(unsigned int, unsigned int);
void print(unsigned long int v)
{
    cout<<hex<<left<<v<<endl;
}

int main(int argv, const char* argc[])
{
    ofstream fout;
    ofstream name_table("database\\names.txt");
    unsigned int magic;
    unsigned int ignore;
    unsigned int object_start;
    unsigned int nt_count;
    unsigned int nt_start;
    unsigned int et_count;
    unsigned int et_start;
    unsigned int it_count;
    unsigned int it_start;
    unsigned int file_length;
    unsigned long int file_guid[4];
    unsigned char H[4];
    string* names;
    string open_fname;
    if (argv > 1)
    {
        open_fname = argc[1];
    }
    else open_fname = "MK11ItemDatabase.unp";

    fin.open(open_fname.c_str(), ios::binary);
    fin>>noskipws;
    magic = read_little(4);
    ignore = read_little(4);
    object_start = read_little(4);
    for (int i = 0; i < 7; i++)
        ignore = read_little(4);
    nt_count = read_little(4);
    names = new string[nt_count];
    nt_start = read_little(4);
    ignore = read_little(4);
    et_count = read_little(4);
    et_start = read_little(4);
    ignore = read_little(4);
    it_count = read_little(4);
    it_start = read_little(4);
    ignore = read_little(4);
    file_length = read_little(4);
    cout<<"Info:\n";
    cout<<"\tNumber of Name Table Entries: ";
    print(nt_count);
    cout<<"\tName Table Start Location: ";
    print(nt_start);
    cout<<"\tNumber of Export Table Entries: ";
    print(et_count);
    cout<<"\tExport Table Start Location: ";
    print(et_start);
    cout<<"\tNumber of Import Table Entries: ";
    print(it_count);
    cout<<"\tImport Table Start Location: ";
    print(it_start);
    cout<<"\tObjects Start Location: ";
    print(object_start);
    cout<<"\tTotal File Length: ";
    print(file_length);

    ignore = read_little(4);
    for (int i = 0; i < 4; i++)
        file_guid[i] = read_little(4);
    cout<<"File GUID:\n";

    for (int i = 0; i < 4; i++)
        print(file_guid[i]);


    //Skip to Name Table
    skip(nt_start);
    cout<<"Names:\n";
    for (unsigned int i = 0; i < nt_count; i++)
    {
        unsigned int name_len = read_little(4);
        names[i] = read_string(name_len);
        name_table<<names[i]<<endl;
        //cout<<names[i]<<endl;
    }

    //Skip to Export Table
    skip(et_start);

    //Start Reading Export Table
    unsigned int import;
    unsigned int name;
    unsigned int type;
    unsigned int length;
    unsigned int start;
    unsigned long int database_length = 0;
    unsigned long int database_start = 0;
    for (int i = 0; i < et_count; i++)
    {
        import = read_little(4);
        ignore = read_little(4);
        name = read_little(4);
        for (int j = 0; j < 8; j++)
            ignore = read_little(4);
        type = read_little(4);
        ignore = read_little(4);
        length = read_little(4);
        start = read_little(4);
        for (int j = 0; j < 4; j++)
            ignore = read_little(4);
        cout<<"Export Entry Info:\n";
        cout<<"\tImport: ";
        print(import);
        cout<<"\tName: ";
        print(name);
        string mapped_name = names[name];
        cout<<"\tMapped Name: "<<mapped_name<<endl;
        cout<<"\tType: ";
        print(type);
        string mapped_type = names[type];
        cout<<"\tMapped Type: "<<mapped_type<<endl;
        cout<<"\tLength: ";
        print(length);
        cout<<"\tStart: ";
        print(start);

        if (!strcmp(mapped_name.c_str(), "MK11ItemDatabase") && !strcmp(mapped_type.c_str(),"Other"))
        {
            database_length = length;
            database_start = start;
        }

    }

    cout<<"Database Info:\n";
    cout<<"\tDatabase Start: ";
    print(database_start);
    cout<<"\tDatabase Length: ";
    print(database_length);

    if (!database_start)
    {
        cerr<<"Couldn't find database";
        return -1;
    }
    //Skip to Database
    skip(database_start);
    unsigned int f_ctr = 0;
    while(read_counter < file_length)
    {
        ignore = read_little(16);
        unsigned long int segment_length = read_little(8);
        cout<<"Segment Length: ";
        print(segment_length);
        cout<<"Segment End: ";
        print(read_counter + segment_length);

        save(read_counter + segment_length, f_ctr);
        //skip(read_counter + segment_length);
        f_ctr++;

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
    ss<<"database\\output_"<<index<<".seg";
    ofstream fout;
    fout.open(ss.str().c_str(), ios::binary);

        //
    fin.seekg(-0x18, ios_base::cur);
    read_counter -= 0x18;
    while(read_counter < save_to)
    {
        fout<<(unsigned char)(read_little(1));
    }
}

string read_string(unsigned int size)
{
    string s = "";
    unsigned char x;
    for (int i = 0; i < size; i++)
    {
        fin>>x;
        s += x;
        read_counter++;
    }
    return s;
}
