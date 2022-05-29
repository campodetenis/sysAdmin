#!/usr/bin/perl 
#falta comprobar que no haya usuarios con el mismo nombre?

use strict; #me da problemas con la palabra true y no puedo insertar booleanos en mysql
use warnings;

use CGI; #para poder incovarlo desde la pagina web
use Linux::usermod; #para crear el usuario
use File::Path qw(make_path remove_tree); #para crear el directorio
use File::chown; #las opciones por defecto de Path no me cambian bien el dueño del directorio
use DBI; #para conectar con la base de datos.
use Email::Send::SMTP::Gmail;
#use Email::Address; #para parsear el correo


#para que funcione el cgi
my $q = CGI->new;
my @row;
#print $q->header();
#parametros de usuario.
my $sth;
my $codigo = $q->param('codigo');
my $user; #para pillar el objeto user de usermod

#conecto con la base de datos global con el usuario gestor cuya contraseña esta vacía.
my $dbh = DBI->connect('DBI:MariaDB:database=global;host=localhost',
                       'gestor','Yg0yubme7jyHzCOf',
                       { RaiseError => 1, PrintError => 0,AutoCommit => 1 });

#busco en la base de datos al usuario con el codigo que se ha introducido.
#Si ningun codigo coincide, entonces error
$sth = $dbh->prepare("SELECT codigo FROM usuarios WHERE codigo=?");
$sth->execute($codigo);

my ($count) = $sth->fetchrow_array();

if(!$count){
    #error
    #borrar la entrada de la base de datos
    #borrar el usuario de usermod.
}else{
    $sth = $dbh->prepare("SELECT nombre FROM usuarios WHERE codigo=?");
    $sth->execute($codigo);
    my ($count) = $sth->fetchrow_array();
    #con el nombre cogemos el hash de usermod y asi le quitamos el nologin
    $user = Linux::usermod->new($count);
    $user->set('shell','/bin/bash');
    #tambien hay que actualizar la base de datos.
    $sth = $dbh->prepare("update usuarios set codigo=0,registrado=1 where codigo=? and nombre=?");
    $sth->execute($codigo, $count);
}
#print "$count";
# si count es null -> error
# si count no es null
# => modifico la entrada con usermod para poner /bin/bash
# => modifico la entrada de la base de datos para cambiar el campo registrado y codigo a 0
$dbh->disconnect;
print $q->redirect('https://www.marca.com/');