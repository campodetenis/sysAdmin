#!/usr/bin/perl 


=pod
*******************************************************
*Cosas por hacer:
*	chown a las carpetas creadas
*	mensaje mas personalizado
*	correo electronico (falta tambien en el html)
*	redireccionar a las paginas que tocan (faltan los htmls)
*	aprender a mandar mensajes de error sin cambiar de pagina.
*	End of script output before headers
*	tratamiento de errores: si crea un usuario pero falla la DB existe un usuario fuera de la DB.
*	verificar que no hay campos vacios (+ mensaje error)
*******************************************************
=cut
#

use strict; #me da problemas con la palabra true y no puedo insertar booleanos en mysql
use warnings;

use CGI; #para poder incovarlo desde la pagina web
use Linux::usermod; #para crear el usuari
oingeuse File::Path qw(make_path remove_tree); #para crear el directorio
use File::chown; #las opciones por defecto de Path no me cambian bien el dueño del directorio
use DBI; #para conectar con la base de datos.
use Email::Send::SMTP::Gmail;
#use Email::Address; #para parsear el correo


#para que funcione el cgi
my $q = CGI->new;

#parametros de usuario.
my $nombre  = $q->param('usuario');
my $contrasena   = $q->param('password');
my $esProfesor = $q->param('esProfesor');
my $correo = $q->param('email');
my $direccion = $q->param('direccion');
my $grupo; #alumno o profesor
my $mensaje = "bienvenido $nombre"; # hay que terminar el mensaje
my $ruta; #ubicacion del directorio del usuario
my $directorio; #directorio del usuario para hacer con make_path
my $codigo = int(rand( 9999-1000+1 ) ) + 1000;

#conseguimos un hash de los usuarios para verificar.
my %usuarios = Linux::usermod->users();
my $sth; #para la base de datos

#compruebo que no haya cadenas vacias y en caso afirmativo redirijo a pagina de error.
if(!$nombre | !$contrasena | !$correo | !$ direccion){
	#redireccionar a una pagina de error
	print $q->redirect('/index.html');
	exit 0;
}

#aqui habria que verificar que el usuario no sea ni root ni repetido.
if($nombre eq "root" or $nombre eq "admin"){
	#redireccionar a una pagina de error
	print $q->redirect('/index.html');
	exit 0;
}

#conecto con la base de datos global con el usuario gestor cuya contraseña esta vacía.
my $dbh = DBI->connect('DBI:MariaDB:database=global;host=localhost',
                       'gestor','Yg0yubme7jyHzCOf',
                       { RaiseError => 1, PrintError => 0 });


#esto estaria guay automatizarlo pero de momento funciona
if($esProfesor){
	$grupo = '1003';
}else{
	$grupo = '1002';
}

for(keys %usuarios){
	if($_ eq $nombre){
		#el usuario ya existe asi que mando error
		print $q->redirect('/index.html');
		exit 0;
	}
}


$sth = $dbh->prepare("insert into usuarios (nombre, isProfesor, email, direccion, codigo, registrado) values (?,?,?,?,?,?)") or die;
if($esProfesor){
	$sth->execute($nombre, 1, $correo, $direccion, $codigo, 0) or die;
}else{
	$sth->execute($nombre, 0, $correo, $direccion, $codigo, 0) or die;
}



$ruta = "/home/$nombre"; 
Linux::usermod->add($nombre,$contrasena,"",$grupo,$mensaje ,$ruta,"nologin");
#system("/usr/bin/perl /perlScripts/directorio.pl $nombre");

#no funciona la parte del chown. Hay que usar ldap o suexec
=pod
$directorio = make_path($ruta,{
	chmod => 0755,
	owner => $nombre,
	group => $grupo,
});
=cut

#gestiono el envio del correo electronico
my ($mail,$error)=Email::Send::SMTP::Gmail->new( -smtp=>'smtp.gmail.com',
                                                 -login=>'pecera.correo@gmail.com',
                                                 -pass=>'21052105');

print "session error: $error" unless ($mail!=-1);
if($mail == -1){
	#error mandando el correo
	print $q->redirect("/index.html"); 	#redirijo a pagina
	Linux::usermod->del($nombre); #borro el usario 
	$sth = $dbh->prepare("delete from usuarios where nombre=?");
	$sth->execute($nombre);#borro la entrada de la base de datos
	$dbh->disconnect;
}else{
	$mail->send(-to=> $correo, -subject=>'Registro', -body=>'tu codigo es'+$codigo, -attachments=>'full_path_to_file');
	$mail->bye;
	print $q->redirect('/correo.html');
}




