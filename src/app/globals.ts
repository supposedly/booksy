import { Injectable } from '@angular/core';

@Injectable()
export class Globals {
    uID: string;
    lID: string;
    rID: string;
    username: string;
    email: string;
    phone: string;
    managesLocation: boolean;
    isCheckoutAccount: boolean;
    isLoggedIn: boolean = false;
}
