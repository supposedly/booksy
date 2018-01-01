import { Component, OnInit, Input } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';

import { MediaItem } from '../classes';
import { CheckoutService } from '../checkout.service';
import { MediaService } from '../media.service';
import { MemberAuthService } from '../member-auth.service';

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html',
  styleUrls: ['./checkout.component.css']
})
export class CheckoutComponent implements OnInit {

  constructor(
    private checkoutService: CheckoutService,
    private mediaService: MediaService,
    private memberAuthService: MemberAuthService,
    private isLibrary: boolean
  ) { }

  ngOnInit() {
    this.isLibrary = this.memberAuthService.isCheckoutAccount;
  }
  
  onSubmit(): void {
    //this.checkoutService.checkOut
  }
}
