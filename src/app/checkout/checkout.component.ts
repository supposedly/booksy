import { Component, OnInit, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { MediaItem } from '../classes';
import { CheckoutService } from '../checkout.service';
import { MediaService } from '../media.service';
import { MemberAuthService } from '../member-auth.service';
import { Globals } from '../globals';

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html',
  styleUrls: ['./checkout.component.css']
})
export class CheckoutComponent implements OnInit {
  isCheckoutAccount: boolean;
  msg: string = null;
  name: string;
  mid: string;
  _mid: string;
  username: string = null;
  
  constructor(
    private checkoutService: CheckoutService,
    private mediaService: MediaService,
    private memberAuthService: MemberAuthService,
    private globals: Globals
  ) {
      this.isCheckoutAccount = globals.isCheckoutAccount;
      if (!this.isCheckoutAccount) {
        this.username = globals.username;
        if (this.globals.managesLocation) {
          this.name = globals.locname + ' Admin'
        } else {
          this.name = globals.name;
        }
      } else {
        this.name = globals.locname + ' Patron'
      }
  }

  ngOnInit() {}
  
  submit(mID): void {
    this._mid = null;
    this.mediaService.getStatus(mID)
      .subscribe(
        status => {
          if (status.available) {
            this.checkoutService.checkOut(mID, this.username).subscribe(
              resp => {
                this.msg = 'Checked out!';
                this._mid = this.mid;
              },
              err => this.msg = err.error?err.error:'Error checking out'
            );
          } else if (this.globals.canReturnItems || (status.issuedTo == this.username && !this.isCheckoutAccount)) {
            this.checkoutService.checkIn(mID, this.username)
              .subscribe(
                resp => {
                  this.msg = 'Checked in!';
                  this._mid = this.mid;
                },
                err => this.msg = err.error?err.error:'Error checking in'
              );
          } else {
            this.msg = 'Item is checked out to ' + status.issuedTo.toString() + '.';
          }
        },
        err => {console.log(err); this.msg = err.error?err.error:'Error checking out'}
      );
  }
}
