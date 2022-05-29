#!/usr/bin/perl

#esto va en todos los script
use strict;
use warnings;

use CGI;
use Linux::usermod;
use Authen::PAM;
use POSIX qw(ttyname);

my $q = CGI->new;
#print $q->header();


my $username = $q->param('email');;
my $service = "passwd";
my $password = $q->param('password');;
my $pamh;


sub my_conv_func {
    my @res;
    while ( @_ ) {
        my $code = shift;
        my $msg = shift;
 		my $ans = '';

 		$ans = $username if ($code == PAM_PROMPT_ECHO_ON());
 		$ans = $password if ($code == PAM_PROMPT_ECHO_OFF());
 
       push @res, (PAM_SUCCESS(),$ans);
    }
    push @res, PAM_SUCCESS();
    return @res;
}


if (!ref($pamh = new Authen::PAM($service, $username, \&my_conv_func))) {
    print "Authen::PAM fallo al iniciar\n";
    exit 1;
}

my $res = $pamh->pam_authenticate;

if($res == PAM_SUCCESS()){
	print $q->redirect('/index.html');
}else{
	print $q->redirect('/errorSign.html');
}
