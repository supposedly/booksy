import { Component, OnInit } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';

import { MediaItem } from '../classes';
import { CheckoutService } from '../checkout.service';

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html',
  styleUrls: ['./checkout.component.css']
})
export class CheckoutComponent implements OnInit {

  constructor(
    private checkoutService: CheckoutService,
    private mediaService: MediaService
  ) { }

  ngOnInit() {
  }
  
  @Input() media: MediaItem;
  
  onSubmit(): void {
    this.checkoutService.postMedia(
  }
}
